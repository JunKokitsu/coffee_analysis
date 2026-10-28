import re
from datetime import date
from pathlib import Path

from ponto_do_cafe.staging.mobility.station_demand_record import StationDemandRecord

LINE_HEADER = re.compile(r"^LINHA (\d+)-")
MONTH_COLUMNS = range(1, 13)
IGNORED_FIRST_CELLS = ("", "Estação", "Total")


class MetroDemandSheet:
    def __init__(self, path: Path) -> None:
        self._year = int(path.stem.rsplit("_", 1)[1])
        self._rows = path.read_text(encoding="latin-1").splitlines()

    def records(self) -> list[StationDemandRecord]:
        records: list[StationDemandRecord] = []
        line_number = 0
        for row in self._rows:
            line_number = self._line_number(row, line_number)
            records = records + self._station_records(row.split(";"), line_number)
        return records

    def _line_number(self, row: str, current_line_number: int) -> int:
        header = LINE_HEADER.match(row)
        if header is None:
            return current_line_number
        return int(header.group(1))

    def _station_records(self, cells: list[str], line_number: int) -> list[StationDemandRecord]:
        station = cells[0].strip()
        if line_number == 0 or station in IGNORED_FIRST_CELLS or len(cells) < 13:
            return []
        return [
            StationDemandRecord(line_number, station, date(self._year, month, 1), self._value(cells[month]))
            for month in MONTH_COLUMNS
            if self._is_number(cells[month])
        ]

    def _is_number(self, cell: str) -> bool:
        return re.fullmatch(r"[\d.]+(,\d+)?", cell.strip()) is not None

    def _value(self, cell: str) -> float:
        return float(cell.strip().replace(".", "").replace(",", "."))
