"""Seeded Indian payments generator with explicit fraud labels for evaluation."""
from __future__ import annotations

import hashlib
import random
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from payinsight.models import BankName, PaymentEvent, PaymentMethod, TransactionStatus

BANKS = tuple(BankName)
METHODS = tuple(PaymentMethod)
CITIES = (("Mumbai", "Maharashtra"), ("Bengaluru", "Karnataka"), ("Delhi", "Delhi"),
          ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"))
CATEGORIES = ("ecommerce", "food_delivery", "travel", "gaming", "utilities", "education")


def _token(prefix: str, seed: int, index: int, width: int = 6) -> str:
    digest = hashlib.sha256(f"{seed}:{prefix}:{index}".encode()).hexdigest()
    return f"{prefix}_{digest[:width]}" if prefix == "txn" else f"{prefix}_{digest[:width].upper()}"


def _ip(seed: int, index: int) -> str:
    digest = hashlib.sha256(f"{seed}:ip:{index}".encode()).digest()
    return ".".join(str(octet) for octet in digest[:4])


def generate_payments(
    n: int = 1_000, seed: int = 42, chunk_size: int = 250,
    start: datetime | None = None,
) -> Iterator[list[PaymentEvent]]:
    """Yield reproducible chunks; ``is_fraud`` is synthetic ground truth only."""
    if n < 0 or chunk_size <= 0:
        raise ValueError("n must be non-negative and chunk_size must be positive")
    rng = random.Random(seed)
    origin = start or datetime(2024, 1, 1, tzinfo=UTC)
    merchants, customers = max(3, n // 50), max(20, n // 4)
    chunk: list[PaymentEvent] = []
    for i in range(n):
        fraud_type = None
        is_fraud = False
        amount = Decimal(f"{rng.uniform(100, 100000):.2f}")
        if i % 113 == 0:
            amount, fraud_type, is_fraud = Decimal("249999.99"), "high_value", True
        if i % 79 == 0:
            fraud_type, is_fraud = "velocity", True
        status = TransactionStatus.FAILED if i % 29 == 0 else (
            TransactionStatus.REFUNDED if i % 101 == 0 else TransactionStatus.SUCCESS
        )
        city, state = CITIES[i % len(CITIES)]
        event = PaymentEvent(
            transaction_id=_token("txn", seed, i, 12), payment_id=_token("pay", seed, i, 12),
            merchant_id=_token("mer", seed, i % merchants), customer_id=_token("cus", seed, i % customers),
            amount_inr=amount, payment_method=METHODS[i % len(METHODS)],
            bank_name=BANKS[i % len(BANKS)], transaction_status=status, status=status,
            merchant_category=CATEGORIES[i % len(CATEGORIES)], city=city, state=state,
            ip_address=_ip(seed, i // 3 if i % 37 == 0 else i),
            device_id=_token("dev", seed, i // 5 if i % 41 == 0 else i, 16),
            created_at=origin + timedelta(minutes=i * 7), is_fraud=is_fraud, fraud_type=fraud_type,
        )
        chunk.append(event)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
