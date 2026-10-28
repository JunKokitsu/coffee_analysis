from pathlib import Path

import geopandas
import pandas
import polars

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

GEOGRAPHIC_PROJECTION = "EPSG:4326"


class DistrictMobility:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        districts = geopandas.read_parquet(self._directories.staging_file("censo_2022", "distritos.parquet"))
        trips = pandas.read_parquet(self._directories.staging_file("pesquisa_od", "viagens.parquet"))
        people = pandas.read_parquet(self._directories.staging_file("pesquisa_od", "pessoas.parquet"))
        self._database.register_frame("viagens_localizadas", self._located(trips, "destino", districts))
        self._database.register_frame("trabalhadores_localizados", self._located(people, "trabalho", districts))
        self._database.export_parquet(self._trips_query(), self._directories.marts_file("viagens_destino.parquet"))
        destination = self._directories.marts_file("distritos_mobilidade.parquet")
        return self._database.export_parquet(self._districts_query(), destination)

    def _located(self, frame: pandas.DataFrame, place: str, districts: geopandas.GeoDataFrame) -> polars.DataFrame:
        known = frame[frame[f"latitude_{place}"].notna()]
        geometry = geopandas.points_from_xy(known[f"longitude_{place}"], known[f"latitude_{place}"])
        points = geopandas.GeoDataFrame(known, geometry=geometry, crs=GEOGRAPHIC_PROJECTION)
        located = geopandas.sjoin(points.to_crs(districts.crs), districts[["codigo_distrito", "geometry"]], how="left", predicate="within")
        return polars.from_pandas(pandas.DataFrame(located.drop(columns=["geometry", "index_right"])))

    def _trips_query(self) -> str:
        return """
            SELECT
                id_pessoa,
                numero_viagem,
                fator_expansao_viagem,
                codigo_motivo_destino,
                motivo_destino,
                CASE
                    WHEN codigo_motivo_destino IN (1, 2, 3) THEN 'trabalho'
                    WHEN codigo_motivo_destino = 4 THEN 'estudo'
                    WHEN codigo_motivo_destino IN (5, 6, 9, 10) THEN 'compras_e_servicos'
                    WHEN codigo_motivo_destino IN (7, 11) THEN 'lazer_e_refeicao'
                    ELSE 'residencia'
                END AS categoria_motivo,
                hora_chegada,
                latitude_destino,
                longitude_destino,
                codigo_distrito
            FROM viagens_localizadas
        """

    def _districts_query(self) -> str:
        districts = self._directories.staging_file("censo_2022", "distritos.parquet")
        trips = self._directories.marts_file("viagens_destino.parquet")
        stations = self._directories.marts_file("estacoes_demanda.parquet")
        return f"""
            WITH viagens AS (
                SELECT
                    codigo_distrito,
                    sum(fator_expansao_viagem) FILTER (WHERE categoria_motivo = 'trabalho') AS viagens_atraidas_trabalho,
                    sum(fator_expansao_viagem) FILTER (WHERE categoria_motivo = 'estudo') AS viagens_atraidas_estudo,
                    sum(fator_expansao_viagem) FILTER (WHERE categoria_motivo = 'compras_e_servicos') AS viagens_atraidas_compras_e_servicos,
                    sum(fator_expansao_viagem) FILTER (WHERE categoria_motivo = 'lazer_e_refeicao') AS viagens_atraidas_lazer_e_refeicao,
                    sum(fator_expansao_viagem) FILTER (WHERE categoria_motivo <> 'residencia') AS viagens_atraidas_nao_residenciais,
                    count(*) FILTER (WHERE categoria_motivo <> 'residencia') AS viagens_atraidas_amostra
                FROM '{trips}'
                WHERE codigo_distrito IS NOT NULL
                GROUP BY codigo_distrito
            ),
            trabalhadores AS (
                SELECT codigo_distrito, sum(fator_expansao_pessoa) AS trabalhadores_no_distrito
                FROM trabalhadores_localizados
                WHERE codigo_distrito IS NOT NULL
                GROUP BY codigo_distrito
            ),
            estacoes AS (
                SELECT
                    codigo_distrito,
                    count(*) AS estacoes_metro_trem,
                    count(*) FILTER (WHERE demanda_media_dias_uteis IS NULL) AS estacoes_sem_demanda,
                    sum(demanda_media_dias_uteis) AS demanda_estacoes_dias_uteis
                FROM '{stations}'
                WHERE codigo_distrito IS NOT NULL
                GROUP BY codigo_distrito
            )
            SELECT
                distritos.codigo_distrito,
                coalesce(viagens.viagens_atraidas_trabalho, 0) AS viagens_atraidas_trabalho,
                coalesce(viagens.viagens_atraidas_estudo, 0) AS viagens_atraidas_estudo,
                coalesce(viagens.viagens_atraidas_compras_e_servicos, 0) AS viagens_atraidas_compras_e_servicos,
                coalesce(viagens.viagens_atraidas_lazer_e_refeicao, 0) AS viagens_atraidas_lazer_e_refeicao,
                coalesce(viagens.viagens_atraidas_nao_residenciais, 0) AS viagens_atraidas_nao_residenciais,
                coalesce(viagens.viagens_atraidas_amostra, 0) AS viagens_atraidas_amostra,
                coalesce(viagens.viagens_atraidas_nao_residenciais, 0) / distritos.populacao_2022 AS viagens_atraidas_por_morador,
                coalesce(trabalhadores.trabalhadores_no_distrito, 0) AS trabalhadores_no_distrito,
                coalesce(estacoes.estacoes_metro_trem, 0) AS estacoes_metro_trem,
                coalesce(estacoes.estacoes_sem_demanda, 0) AS estacoes_sem_demanda,
                coalesce(estacoes.demanda_estacoes_dias_uteis, 0) AS demanda_estacoes_dias_uteis
            FROM (SELECT codigo_distrito, populacao_2022 FROM '{districts}') AS distritos
            LEFT JOIN viagens USING (codigo_distrito)
            LEFT JOIN trabalhadores USING (codigo_distrito)
            LEFT JOIN estacoes USING (codigo_distrito)
            ORDER BY distritos.codigo_distrito
        """
