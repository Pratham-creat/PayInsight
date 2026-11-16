"""Generate realistic, reproducible payment events without external data."""
from __future__ import annotations

import hashlib
import random
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from payinsight.models import PaymentEvent, PaymentMethod, PaymentStatus

COUNTRIES = ("US", "GB", "CA", "DE", "AU", "SG")
CATEGORIES = ("retail", "travel", "digital_goods", "gaming", "marketplace")
METHODS = tuple(PaymentMethod)


def _token(prefix: str, seed: int, index: int, width: int = 6) -> str:
    digest = hashlib.sha256(f"{seed}:{prefix}:{index}".encode()).hexdigest()
    if prefix != "pay":
        digest = digest.upper()
    return f"{prefix}_{digest[:width]}"


def _ip(seed: int, index: int) -> str:
    digest = hashlib.sha256(f"{seed}:ip:{index}".encode()).digest()
    return f"{digest[0]}.{digest[1]}.{digest[2]}.{digest[3]}"


def generate_payments(
    n: int = 1_000,
    seed: int = 42,
    chunk_size: int = 250,
    start: datetime | None = None,
) -> Iterator[list[PaymentEvent]]:
    """Yield deterministic payment chunks, including intentional fraud-like signals."""
    if n < 0 or chunk_size <= 0:
        raise ValueError("n must be non-negative and chunk_size must be positive")
    rng = random.Random(seed)
    origin = start or datetime(2024, 1, 1, tzinfo=UTC)
    chunk: list[PaymentEvent] = []
    merchants = max(3, n // 50)
    customers = max(20, n // 4)
    for i in range(n):
        amount = Decimal(f"{rng.uniform(4, 950):.2f}")
        # A stable set of anomalies makes demos and tests useful.
        if i % 113 == 0:
            amount = Decimal("4999.99")
        status = PaymentStatus.failed if i % 29 == 0 else PaymentStatus.succeeded
        method = METHODS[i % len(METHODS)]
        if i % 47 == 0:
            method = PaymentMethod.card
        event = PaymentEvent(
            payment_id=_token("pay", seed, i, 12),
            merchant_id=_token("mer", seed, i % merchants),
            customer_id=_token("cus", seed, i % customers),
            amount=amount,
            currency="USD" if i % 17 else "EUR",
            status=status,
            payment_method=method,
            merchant_category=CATEGORIES[i % len(CATEGORIES)],
            country=COUNTRIES[i % len(COUNTRIES)],
            ip_address=_ip(seed, i // 3 if i % 37 == 0 else i),
            device_id=_token("dev", seed, i // 5 if i % 41 == 0 else i, 16),
            created_at=origin + timedelta(minutes=i * 7),
        )
        chunk.append(event)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
