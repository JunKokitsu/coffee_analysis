from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.metro_demand_sheet import MetroDemandSheet
from coffee_analysis.station_demand_table import StationDemandTable


class MetroStationDemand:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._table = StationDemandTable(database)
        self._directories = directories

    def build(self) -> Path:
        competence = self._directories.raw_competence("metro")
        sheets = [MetroDemandSheet(path) for path in sorted(competence.glob("demanda_estacoes_*.csv"))]
        records = [record for sheet in sheets for record in sheet.records()]
        return self._table.export(records, self._directories.staging_file("metro", "demanda_estacoes.parquet"))
