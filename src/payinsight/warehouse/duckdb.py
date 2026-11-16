"""Small DuckDB repository for local analytics and API reads."""
from pathlib import Path

import duckdb
import polars as pl


class PaymentWarehouse:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.connection = duckdb.connect(str(path))

    def load(self, frame: pl.DataFrame) -> None:
        self.connection.register("incoming_payments", frame.to_arrow())
        self.connection.execute(
            "CREATE OR REPLACE TABLE payments AS SELECT * FROM incoming_payments"
        )
        self.connection.unregister("incoming_payments")

    def query(self, sql: str) -> pl.DataFrame:
        return pl.from_arrow(self.connection.execute(sql).to_arrow_table())

    def close(self) -> None:
        self.connection.close()
