from collections.abc import Iterable

from payinsight.models import PaymentEvent


def ingest_events(events: Iterable[PaymentEvent]) -> list[PaymentEvent]:
    return list(events)
