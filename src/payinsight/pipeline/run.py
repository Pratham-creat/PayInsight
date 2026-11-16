"""Build the in-memory demo dataset used by the API and CLI."""
from payinsight.generator.seeded import generate_payments
from payinsight.pipeline.stages import build_features, payments_frame, validate_payments
from payinsight.warehouse.duckdb import PaymentWarehouse


def build_demo(count: int = 1_000) -> tuple[PaymentWarehouse, list]:
    events = [event for chunk in generate_payments(count) for event in chunk]
    frame = build_features(validate_payments(payments_frame(events)))
    warehouse = PaymentWarehouse()
    warehouse.load(frame)
    return warehouse, events
