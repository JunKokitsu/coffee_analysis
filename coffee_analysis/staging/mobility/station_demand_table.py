from pathlib import Path

import polars

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.staging.mobility.station_demand_record import StationDemandRecord
from coffee_analysis.staging.mobility.station_name_key import StationNameKey

PASSENGERS_PER_THOUSAND = 1000


class StationDemandTable:
    def __init__(self, database: AnalyticalDatabase) -> None:
        self._database = database
        self._key = StationNameKey()

    def export(self, records: list[StationDemandRecord], destination: Path) -> Path:
        frame = polars.DataFrame(records)
        self._database.register_frame("demanda_estacoes_bruta", frame)
        return self._database.export_parquet(self._query(), destination)

    def _query(self) -> str:
        return f"""
            SELECT
                numero_linha::INTEGER AS numero_linha,
                any_value({self._key.display_name("nome_estacao")}) AS nome_estacao,
                {self._key.expression("nome_estacao")} AS chave_estacao,
                competencia::DATE AS competencia,
                avg(demanda_media_dias_uteis) * {PASSENGERS_PER_THOUSAND} AS demanda_media_dias_uteis
            FROM demanda_estacoes_bruta
            GROUP BY numero_linha, chave_estacao, competencia
            ORDER BY numero_linha, chave_estacao, competencia
        """
