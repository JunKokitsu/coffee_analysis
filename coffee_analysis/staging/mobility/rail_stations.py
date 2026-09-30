from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.mobility.station_name_key import StationNameKey

STATION_LAYERS = ("estacao_metro", "estacao_trem")
OPERATING_STATUS = "OPERANDO"


class RailStations:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories
        self._key = StationNameKey()

    def build(self) -> Path:
        destination = self._directories.staging_file("geosampa", "estacoes_metro_trem.parquet")
        return self._database.export_parquet(self._query(), destination)

    def _query(self) -> str:
        competence = self._directories.raw_competence("geosampa")
        sources = ", ".join(f"'{competence / f'{layer}.json'}'" for layer in STATION_LAYERS)
        return f"""
            WITH feicoes AS (
                SELECT unnest(features) AS feicao
                FROM read_json([{sources}], maximum_object_size = 100000000)
            ),
            estacoes AS (
                SELECT
                    feicao.properties.cd_identificador_linha::INTEGER AS numero_linha,
                    feicao.properties.nm_linha_metro_trem AS nome_linha,
                    feicao.properties.nm_empresa_metro_trem AS operadora,
                    feicao.properties.nm_estacao_metro_trem AS nome_estacao,
                    feicao.properties.tx_situacao_metro_trem AS situacao,
                    feicao.geometry.coordinates[1]::DOUBLE AS longitude,
                    feicao.geometry.coordinates[2]::DOUBLE AS latitude
                FROM feicoes
            )
            SELECT
                numero_linha,
                nome_linha,
                operadora,
                any_value(nome_estacao) AS nome_estacao,
                {self._key.expression("nome_estacao")} AS chave_estacao,
                avg(latitude) AS latitude,
                avg(longitude) AS longitude
            FROM estacoes
            WHERE situacao = '{OPERATING_STATUS}'
            GROUP BY numero_linha, nome_linha, operadora, chave_estacao
            ORDER BY numero_linha, chave_estacao
        """
