"""Pipeline stages: validate, normalise, enrich, and aggregate."""
from collections import defaultdict
from decimal import Decimal

from payinsight.models import PayrollEvent


def validate(events: list[PayrollEvent]) -> list[PayrollEvent]:
    return [e for e in events if e.gross_pay >= e.net_pay >= 0 and e.hours >= 0]

def normalize(events: list[PayrollEvent]) -> list[PayrollEvent]:
    return [e.model_copy(update={"gross_pay": e.gross_pay.quantize(Decimal("0.01")),
                                  "net_pay": e.net_pay.quantize(Decimal("0.01"))}) for e in events]

def enrich(events: list[PayrollEvent]) -> list[dict]:
    return [{**e.model_dump(mode="json"), "net_ratio": float(e.net_pay / e.gross_pay) if e.gross_pay else 0.0,
             "is_low_hours": e.hours < 20} for e in events]

def aggregate(events: list[PayrollEvent]) -> list[dict]:
    totals = defaultdict(lambda: {"employee_id": "", "event_count": 0, "gross_total": Decimal(0), "net_total": Decimal(0)})
    for e in events:
        row = totals[e.employee_id]
        row["employee_id"], row["event_count"] = e.employee_id, row["event_count"] + 1
        row["gross_total"] += e.gross_pay
        row["net_total"] += e.net_pay
    return list(totals.values())
