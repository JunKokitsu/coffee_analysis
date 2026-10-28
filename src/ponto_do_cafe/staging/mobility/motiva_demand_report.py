import logging
import re
from datetime import date
from pathlib import Path

import pypdf

from ponto_do_cafe.staging.mobility.station_demand_record import StationDemandRecord

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
COMPETENCE_PATTERN = re.compile(r"demanda\s*-\s*(\w+)\s*(?:de\s*)?(\d{4})", re.IGNORECASE)
LINE_PATTERN = re.compile(r"Linha\s*(\d+)")
STATION_PATTERN = re.compile(r"^(.+?)[¹²³⁴⁵⁶⁷⁸⁹]*\s+(\d+(?:,\d+)?)\s*$", re.MULTILINE)
MINIMUM_STATIONS = 5


class MotivaDemandReport:
    def __init__(self, path: Path) -> None:
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        reader = pypdf.PdfReader(path)
        self._text = "\n".join(page.extract_text() for page in reader.pages)

    def records(self) -> list[StationDemandRecord]:
        competence = COMPETENCE_PATTERN.search(self._text)
        line = LINE_PATTERN.search(self._text)
        stations = [station for station in STATION_PATTERN.findall(self._text) if self._is_station(station[0])]
        if competence is None or line is None or len(stations) < MINIMUM_STATIONS:
            return []
        month = MONTHS[competence.group(1).lower()]
        first_day = date(int(competence.group(2)), month, 1)
        line_number = int(line.group(1))
        return [StationDemandRecord(line_number, name.strip(), first_day, float(value.replace(",", "."))) for name, value in stations]

    def _is_station(self, name: str) -> bool:
        normalized = name.strip().lower()
        return normalized != "total" and "demanda" not in normalized
