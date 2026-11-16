from payinsight.models import PaymentEvent


def clean_events(events: list[PaymentEvent]) -> list[PaymentEvent]:
    return [event for event in events if not event.dirty_row]
