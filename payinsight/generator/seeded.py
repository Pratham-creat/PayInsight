"""Deterministic, chunked synthetic payroll event generator."""
import hashlib
import random
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from payinsight.models import PayrollEvent


def _account(seed: int, employee: int) -> str:
    return hashlib.sha256(f"{seed}:{employee}".encode()).hexdigest()[:16]

def generate_events(n: int = 1000, seed: int = 42, chunk_size: int = 250) -> Iterator[list[PayrollEvent]]:
    """Yield reproducible lists of events without materialising the full dataset."""
    if n < 0 or chunk_size <= 0:
        raise ValueError("n must be non-negative and chunk_size must be positive")
    rng = random.Random(seed)
    events: list[PayrollEvent] = []
    for i in range(n):
        employee_num = (i % max(1, n // 10 + 1)) + 1
        gross = Decimal(str(rng.randint(1800, 9000)))
        hours = Decimal(str(rng.choice([80, 120, 160, 200])))
        net = (gross * Decimal("0.72")).quantize(Decimal("0.01"))
        # A small deterministic anomaly population helps demonstrate the rules.
        if i % 97 == 0:
            hours = Decimal(1)
        events.append(PayrollEvent(
            employee_id=f"E{employee_num:05d}", employer_id="EMP001",
            pay_date=date(2024, 1, 1) + timedelta(days=(i // 14) * 14),
            gross_pay=gross, net_pay=net, hours=hours,
            bank_account_hash=_account(seed, employee_num),
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i),
        ))
        if len(events) == chunk_size:
            yield events
            events = []
    if events:
        yield events

