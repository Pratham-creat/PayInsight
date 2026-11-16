"""DuckDB repository. Every user value is bound as a parameter."""
from pathlib import Path

import duckdb
import polars as pl


class PaymentWarehouse:
    def __init__(self, path: str | Path = ":memory:"):
        self.connection = duckdb.connect(str(path))

    def load(self, frame: pl.DataFrame) -> None:
        self.connection.register("incoming_payments", frame.to_arrow())
        self.connection.execute("CREATE OR REPLACE TABLE payments AS SELECT * FROM incoming_payments")
        self.connection.unregister("incoming_payments")

    def query(self, sql: str, params: list | tuple = ()) -> pl.DataFrame:
        return pl.from_arrow(self.connection.execute(sql, params).to_arrow_table())

    def close(self) -> None:
        self.connection.close()
