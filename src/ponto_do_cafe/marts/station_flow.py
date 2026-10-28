from pathlib import Path

import geopandas

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

GEOGRAPHIC_PROJECTION = "EPSG:4326"
RECENT_MONTHS = 12


class StationFlow:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        stations = self._database.frame(self._query()).to_pandas()
        points = geopandas.GeoDataFrame(
            stations,
            geometry=geopandas.points_from_xy(stations["longitude"], stations["latitude"]),
            crs=GEOGRAPHIC_PROJECTION,
        )
        districts = geopandas.read_parquet(self._directories.staging_file("censo_2022", "distritos.parquet"))
        located = geopandas.sjoin(points.to_crs(districts.crs), districts[["codigo_distrito", "geometry"]], how="left", predicate="within")
        destination = self._directories.marts_file("estacoes_demanda.parquet")
        located.drop(columns=["geometry", "index_right"]).to_parquet(destination, index=False)
        return destination

    def _query(self) -> str:
        stations = self._directories.staging_file("geosampa", "estacoes_metro_trem.parquet")
        metro = self._directories.staging_file("metro", "demanda_estacoes.parquet")
        motiva = self._directories.staging_file("motiva", "demanda_estacoes.parquet")
        return f"""
            WITH demanda AS (
                SELECT * FROM '{metro}'
                UNION ALL
                SELECT * FROM '{motiva}'
            ),
            ultima_competencia AS (
                SELECT numero_linha, max(competencia) AS competencia FROM demanda GROUP BY numero_linha
            ),
            recente AS (
                SELECT
                    demanda.numero_linha,
                    demanda.chave_estacao,
                    avg(demanda.demanda_media_dias_uteis) AS demanda_media_dias_uteis,
                    count(*) AS meses_com_demanda,
                    max(demanda.competencia) AS ultima_competencia
                FROM demanda
                JOIN ultima_competencia USING (numero_linha)
                WHERE demanda.competencia > ultima_competencia.competencia - INTERVAL {RECENT_MONTHS} MONTH
                GROUP BY ALL
            ),
            candidatos AS (
                SELECT
                    estacoes.*,
                    recente.demanda_media_dias_uteis,
                    recente.meses_com_demanda,
                    recente.ultima_competencia,
                    row_number() OVER (
                        PARTITION BY estacoes.numero_linha, estacoes.chave_estacao
                        ORDER BY (recente.chave_estacao = estacoes.chave_estacao) DESC, recente.demanda_media_dias_uteis DESC
                    ) AS ordem
                FROM '{stations}' AS estacoes
                LEFT JOIN recente
                    ON recente.numero_linha = estacoes.numero_linha
                    AND (
                        list_has_all(string_split(recente.chave_estacao, ' '), string_split(estacoes.chave_estacao, ' '))
                        OR list_has_all(string_split(estacoes.chave_estacao, ' '), string_split(recente.chave_estacao, ' '))
                    )
            )
            SELECT * EXCLUDE (ordem)
            FROM candidatos
            WHERE ordem = 1
            ORDER BY numero_linha, chave_estacao
        """
