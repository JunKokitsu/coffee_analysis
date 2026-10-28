from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.mobility.motiva_demand_report import MotivaDemandReport
from ponto_do_cafe.staging.mobility.station_demand_table import StationDemandTable


class MotivaStationDemand:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._table = StationDemandTable(database)
        self._directories = directories

    def build(self) -> Path:
        competence = self._directories.raw_competence("motiva")
        reports = [MotivaDemandReport(path) for path in sorted(competence.rglob("*.pdf"))]
        records = [record for report in reports for record in report.records()]
        return self._table.export(records, self._directories.staging_file("motiva", "demanda_estacoes.parquet"))
