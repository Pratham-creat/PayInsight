from payinsight.generator.seeded import generate_payments
from payinsight.pipeline.stages import build_features, payments_frame, validate_payments


def test_pipeline_validates_and_builds_features():
    events = [event for chunk in generate_payments(20) for event in chunk]
    frame = build_features(validate_payments(payments_frame(events)))
    assert frame.height == 20
    assert {"amount_log", "customer_payment_count", "is_high_amount"} <= set(frame.columns)
