"""Export the seeded pipeline to Parquet or CSV."""
import argparse
from pathlib import Path

from payinsight.generator.seeded import generate_payments
from payinsight.pipeline.stages import build_features, payments_frame, validate_payments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/payments.parquet"))
    args = parser.parse_args()
    events = [e for chunk in generate_payments(args.rows, args.seed) for e in chunk]
    frame = build_features(validate_payments(payments_frame(events)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.write_csv(args.output) if args.output.suffix == ".csv" else frame.write_parquet(args.output)
