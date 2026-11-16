"""Pipeline command: `payinsight-pipeline --rows 1000 --seed 42 --stage full`."""
import argparse
from pathlib import Path

from payinsight.generator.seeded import generate_payments
from payinsight.pipeline.stages import build_features, payments_frame, validate_payments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stage", choices=("generate", "validate", "features", "full"), default="full")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    events = [row for chunk in generate_payments(args.rows, seed=args.seed) for row in chunk]
    frame = payments_frame(events)
    if args.stage in {"validate", "features", "full"}:
        validate_payments(frame)
    if args.stage in {"features", "full"}:
        frame = build_features(frame)
    if args.output:
        frame.write_parquet(args.output)
    print({"rows": frame.height, "stage": args.stage, "columns": frame.columns})


if __name__ == "__main__":
    main()
