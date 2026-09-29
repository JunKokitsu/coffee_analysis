from pathlib import Path

import polars

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.table_expectation import TableExpectation


def count(database: AnalyticalDatabase, query: str) -> int:
    return int(database.frame(query).item())


def test_detects_nulls_duplicates_and_orphan_districts(tmp_path: Path) -> None:
    table = tmp_path / "tabela.parquet"
    districts = tmp_path / "distritos.parquet"
    polars.DataFrame({"cep": ["01000000", "01000000", None], "codigo_distrito": ["1", "9", "1"]}).write_parquet(table)
    polars.DataFrame({"codigo_distrito": ["1", "2"]}).write_parquet(districts)
    expectation = TableExpectation("teste", table, ("cep", "codigo_distrito"), ("cep",), ("cep",), 5, "codigo_distrito")
    database = AnalyticalDatabase()
    assert not expectation.not_null_result(count(database, expectation.not_null_query())).passed
    assert not expectation.duplicates_result(count(database, expectation.duplicates_query())).passed
    assert not expectation.orphan_districts_result(count(database, expectation.orphan_districts_query(districts))).passed
    assert not expectation.minimum_rows_result(count(database, expectation.volume_query())).passed
    assert not expectation.schema_result(["cep"]).passed


def test_volume_change_respects_tolerance(tmp_path: Path) -> None:
    expectation = TableExpectation("teste", tmp_path / "tabela.parquet", ("cep",), volume_tolerance=0.1)
    assert expectation.volume_change_result(105, 100).passed
    assert not expectation.volume_change_result(80, 100).passed
    assert expectation.volume_change_result(80, None).passed
