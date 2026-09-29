from dataclasses import dataclass
from pathlib import Path

from coffee_analysis.quality_result import QualityResult

DEFAULT_VOLUME_TOLERANCE = 0.3


@dataclass(frozen=True)
class TableExpectation:
    table: str
    path: Path
    required_columns: tuple[str, ...]
    not_null_columns: tuple[str, ...] = ()
    unique_columns: tuple[str, ...] = ()
    minimum_rows: int = 1
    district_column: str | None = None
    volume_tolerance: float = DEFAULT_VOLUME_TOLERANCE

    def schema_result(self, existing_columns: list[str]) -> QualityResult:
        missing = [column for column in self.required_columns if column not in existing_columns]
        return QualityResult(self.table, "esquema", not missing, f"colunas ausentes: {missing}")

    def volume_query(self) -> str:
        return f"SELECT count(*) FROM '{self.path}'"

    def minimum_rows_result(self, rows: int) -> QualityResult:
        return QualityResult(self.table, "volume_minimo", rows >= self.minimum_rows, f"{rows} linhas (mínimo {self.minimum_rows})")

    def not_null_query(self) -> str:
        if not self.not_null_columns:
            return "SELECT 0"
        condition = " OR ".join(f"{column} IS NULL" for column in self.not_null_columns)
        return f"SELECT count(*) FILTER (WHERE {condition}) FROM '{self.path}'"

    def not_null_result(self, null_rows: int) -> QualityResult:
        return QualityResult(self.table, "chaves_nao_nulas", null_rows == 0, f"{null_rows} linhas com nulo em {list(self.not_null_columns)}")

    def duplicates_query(self) -> str:
        if not self.unique_columns:
            return "SELECT 0"
        columns = ", ".join(self.unique_columns)
        return f"SELECT count(*) - count(DISTINCT ({columns})) FROM '{self.path}'"

    def duplicates_result(self, duplicated_rows: int) -> QualityResult:
        return QualityResult(self.table, "chaves_unicas", duplicated_rows == 0, f"{duplicated_rows} linhas duplicadas em {list(self.unique_columns)}")

    def orphan_districts_query(self, districts: Path) -> str:
        column = self.district_column
        return f"""
            SELECT count(*)
            FROM '{self.path}'
            WHERE {column} IS NOT NULL AND {column} NOT IN (SELECT codigo_distrito FROM '{districts}')
        """

    def orphan_districts_result(self, orphan_rows: int) -> QualityResult:
        return QualityResult(self.table, "integridade_distrito", orphan_rows == 0, f"{orphan_rows} linhas com distrito fora da malha do Censo 2022")

    def volume_change_result(self, rows: int, previous_rows: int | None) -> QualityResult:
        if previous_rows is None or previous_rows == 0:
            return QualityResult(self.table, "variacao_volume", True, "sem competência anterior para comparar")
        change = rows / previous_rows - 1
        detail = f"{change:+.1%} contra a competência anterior (tolerância {self.volume_tolerance:.0%})"
        return QualityResult(self.table, "variacao_volume", abs(change) <= self.volume_tolerance, detail)
