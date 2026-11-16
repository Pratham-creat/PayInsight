from pathlib import Path

import duckdb

from payinsight.models import PayrollEvent

SCHEMA = """CREATE TABLE IF NOT EXISTS payroll_events (
 employee_id VARCHAR, employer_id VARCHAR, pay_date DATE, gross_pay DECIMAL(18,2),
 net_pay DECIMAL(18,2), hours DECIMAL(10,2), bank_account_hash VARCHAR, created_at TIMESTAMP
)"""

class Warehouse:
    def __init__(self, path: str = ":memory:"):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(path)
        self.connection.execute(SCHEMA)

    def load(self, events: list[PayrollEvent]) -> int:
        self.connection.executemany("INSERT INTO payroll_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(e.employee_id, e.employer_id, e.pay_date, e.gross_pay, e.net_pay, e.hours, e.bank_account_hash, e.created_at) for e in events])
        return len(events)

    def query(self, sql: str, params: list | None = None) -> list[tuple]:
        return self.connection.execute(sql, params or []).fetchall()

    def close(self) -> None:
        self.connection.close()
