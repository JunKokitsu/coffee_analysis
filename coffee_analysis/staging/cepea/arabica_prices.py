import re
from datetime import date, timedelta
from pathlib import Path

import polars
import requests

from coffee_analysis.infrastructure.data_directories import DataDirectories

FIRST_TABLE_PATTERN = re.compile(r"<table[^>]*>.*?(\d{2}/\d{2}/\d{4}).*?</td>\s*<td[^>]*>\s*([\d.]+,\d{2})", re.DOTALL)
QUOTE_ADDRESS = "https://www.noticiasagricolas.com.br/cotacoes/cafe/indicador-cepea-esalq-cafe-arabica"
MONTHS_OF_HISTORY = 13


class ArabicaPrices:
    def __init__(self, directories: DataDirectories, reference_date: date) -> None:
        self._directories = directories
        self._reference_date = reference_date

    def build(self) -> Path:
        pages = [self._download(quote_date) for quote_date in self._quote_dates()]
        quotes = [self._quote(page) for page in pages]
        valid_quotes = [quote for quote in quotes if quote is not None]
        frame = polars.DataFrame(valid_quotes, schema=["data", "preco_saca_60kg"], orient="row")
        unique_frame = frame.unique(subset="data")
        sorted_frame = unique_frame.sort("data")
        destination = self._directories.staging_file("cepea", "arabica.parquet")
        sorted_frame.write_parquet(destination)
        return destination

    def _quote_dates(self) -> list[date]:
        month_starts = [self._month_start(months_back) for months_back in range(MONTHS_OF_HISTORY)]
        candidate_dates = [month_start.replace(day=22) for month_start in month_starts]
        return [self._previous_weekday(candidate) for candidate in candidate_dates if candidate < self._reference_date]

    def _month_start(self, months_back: int) -> date:
        month_index = self._reference_date.year * 12 + self._reference_date.month - 1 - months_back
        return date(month_index // 12, month_index % 12 + 1, 1)

    def _previous_weekday(self, candidate: date) -> date:
        weekend_offset = max(candidate.weekday() - 4, 0)
        return candidate - timedelta(days=weekend_offset)

    def _download(self, quote_date: date) -> Path:
        destination = self._directories.raw_file("cepea", f"arabica_{quote_date.isoformat()}.html")
        if destination.exists():
            return destination
        response = requests.get(f"{QUOTE_ADDRESS}/{quote_date.isoformat()}", headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        response.raise_for_status()
        destination.write_bytes(response.content)
        return destination

    def _quote(self, page: Path) -> tuple[date, float] | None:
        content = page.read_text(encoding="utf-8", errors="ignore")
        match = FIRST_TABLE_PATTERN.search(content)
        if match is None:
            return None
        date_text = match.group(1)
        day, month, year = date_text.split("/")
        quote_date = date(int(year), int(month), int(day))
        price_text = match.group(2)
        price_without_thousands = price_text.replace(".", "")
        price = float(price_without_thousands.replace(",", "."))
        return quote_date, price
