from pathlib import Path

import duckdb
import polars


class AnalyticalDatabase:
    def __init__(self) -> None:
        self._connection = duckdb.connect()
        self._connection.execute("SET preserve_insertion_order = false")

    def execute(self, query: str) -> None:
        self._connection.execute(query)

    def export_parquet(self, query: str, destination: Path) -> Path:
        self._connection.execute(f"COPY ({query}) TO '{destination}' (FORMAT parquet)")
        return destination

    def frame(self, query: str) -> polars.DataFrame:
        relation = self._connection.sql(query)
        return relation.pl()

    def register_frame(self, name: str, frame: polars.DataFrame) -> None:
        self._connection.register(name, frame)
