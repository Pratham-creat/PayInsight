"""Offline evaluation against generator ground truth."""
from .engine import RiskEngine


def evaluate(events: list) -> dict:
    predictions = RiskEngine(events).assess_all()
    flagged = {key for key, result in predictions.items() if result.risk_band in {"high", "critical"}}
    actual = {event.transaction_id for event in events if event.is_fraud}
    tp = len(flagged & actual)
    return {
        "true_positives": tp,
        "false_positives": len(flagged - actual),
        "false_negatives": len(actual - flagged),
        "precision": tp / len(flagged) if flagged else 0.0,
        "recall": tp / len(actual) if actual else 0.0,
    }
