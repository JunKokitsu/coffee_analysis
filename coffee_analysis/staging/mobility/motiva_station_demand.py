from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.mobility.motiva_demand_report import MotivaDemandReport
from coffee_analysis.staging.mobility.station_demand_table import StationDemandTable


class MotivaStationDemand:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._table = StationDemandTable(database)
        self._directories = directories

    def build(self) -> Path:
        competence = self._directories.raw_competence("motiva")
        reports = [MotivaDemandReport(path) for path in sorted(competence.rglob("*.pdf"))]
        records = [record for report in reports for record in report.records()]
        return self._table.export(records, self._directories.staging_file("motiva", "demanda_estacoes.parquet"))
