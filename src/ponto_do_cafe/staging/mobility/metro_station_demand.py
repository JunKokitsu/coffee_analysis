from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.mobility.metro_demand_sheet import MetroDemandSheet
from ponto_do_cafe.staging.mobility.station_demand_table import StationDemandTable


class MetroStationDemand:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._table = StationDemandTable(database)
        self._directories = directories

    def build(self) -> Path:
        competence = self._directories.raw_competence("metro")
        sheets = [MetroDemandSheet(path) for path in sorted(competence.glob("demanda_estacoes_*.csv"))]
        records = [record for sheet in sheets for record in sheet.records()]
        return self._table.export(records, self._directories.staging_file("metro", "demanda_estacoes.parquet"))
