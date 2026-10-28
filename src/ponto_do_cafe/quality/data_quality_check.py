from pathlib import Path

import polars

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.quality.data_quality_error import DataQualityError
from ponto_do_cafe.quality.quality_result import QualityResult
from ponto_do_cafe.quality.quality_results import QualityResults
from ponto_do_cafe.quality.table_expectation import TableExpectation
from ponto_do_cafe.quality.table_expectations import TableExpectations

HISTORY_FILE = "historico_volumes.parquet"


class DataQualityCheck:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories
        self._districts = directories.staging_file("censo_2022", "distritos.parquet")

    def build(self) -> Path:
        history = self._history()
        volumes = {expectation.table: self._count(expectation.volume_query()) for expectation in self._present_expectations()}
        results = QualityResults(tuple(result for expectation in TableExpectations(self._directories) for result in self._check(expectation, volumes, history)))
        destination = self._directories.quality_file(f"resultado_{self._directories.competence}.parquet")
        results.frame(self._directories.competence).write_parquet(destination)
        failures = results.failure_lines()
        if failures:
            raise DataQualityError(failures)
        self._save_history(history, volumes)
        return destination

    def _present_expectations(self) -> list[TableExpectation]:
        return [expectation for expectation in TableExpectations(self._directories) if expectation.path.exists()]

    def _check(self, expectation: TableExpectation, volumes: dict[str, int], history: polars.DataFrame) -> list[QualityResult]:
        if not expectation.path.exists():
            return [QualityResult(expectation.table, "arquivo", False, f"arquivo ausente: {expectation.path}")]
        rows = volumes[expectation.table]
        results = [
            expectation.schema_result(self._columns(expectation.path)),
            expectation.minimum_rows_result(rows),
            expectation.not_null_result(self._count(expectation.not_null_query())),
            expectation.duplicates_result(self._count(expectation.duplicates_query())),
            expectation.volume_change_result(rows, self._previous_rows(history, expectation.table)),
        ]
        if expectation.district_column is None:
            return results
        return [*results, expectation.orphan_districts_result(self._count(expectation.orphan_districts_query(self._districts)))]

    def _columns(self, path: Path) -> list[str]:
        description = self._database.frame(f"DESCRIBE SELECT * FROM '{path}'")
        return description["column_name"].to_list()

    def _count(self, query: str) -> int:
        frame = self._database.frame(query)
        return int(frame.item())

    def _history(self) -> polars.DataFrame:
        path = self._directories.quality_file(HISTORY_FILE)
        if not path.exists():
            return polars.DataFrame(schema={"competencia": polars.String, "tabela": polars.String, "linhas": polars.Int64})
        return polars.read_parquet(path)

    def _previous_rows(self, history: polars.DataFrame, table: str) -> int | None:
        previous = history.filter((polars.col("tabela") == table) & (polars.col("competencia") < self._directories.competence))
        if previous.is_empty():
            return None
        latest = previous.sort("competencia")
        return int(latest["linhas"][-1])

    def _save_history(self, history: polars.DataFrame, volumes: dict[str, int]) -> Path:
        current = polars.DataFrame(
            {"competencia": [self._directories.competence] * len(volumes), "tabela": list(volumes), "linhas": list(volumes.values())},
            schema={"competencia": polars.String, "tabela": polars.String, "linhas": polars.Int64},
        )
        kept = history.filter(polars.col("competencia") != self._directories.competence)
        destination = self._directories.quality_file(HISTORY_FILE)
        polars.concat([kept, current]).sort("competencia", "tabela").write_parquet(destination)
        return destination
