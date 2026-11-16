from payinsight.models import PaymentEvent
from payinsight.pipeline.stages import payments_frame, validate_payments


def validate_events(events: list[PaymentEvent]):
    return validate_payments(payments_frame(events))
