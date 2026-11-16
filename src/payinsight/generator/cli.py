"""Command line entrypoint for generating a JSONL fixture."""
import argparse
import json
from pathlib import Path

from .seeded import generate_payments


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic payment JSONL")
    parser.add_argument("--count", type=int, default=1_000)
    parser.add_argument("--output", type=Path, default=Path("data/payments.jsonl"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for chunk in generate_payments(args.count):
            for payment in chunk:
                handle.write(json.dumps(payment.model_dump(mode="json")) + "\n")
