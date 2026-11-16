"""Composable pipeline facade retained for batch callers."""
from payinsight.generator.seeded import generate_payments

from .stages import build_features, payments_frame, validate_payments


def run(rows: int = 1000, seed: int = 42, stage: str = "full"):
    events = [event for chunk in generate_payments(rows, seed) for event in chunk]
    frame = payments_frame(events)
    if stage in {"validate", "features", "full"}:
        validate_payments(frame)
    return build_features(frame) if stage in {"features", "full"} else frame
