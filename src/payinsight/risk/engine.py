"""Rules and an optional calibrated scikit-learn anomaly model."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest

from payinsight.models import PaymentEvent, PaymentRisk, RiskFinding


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    points: float
    message: str


RULES = {
    "HIGH_AMOUNT": Rule("HIGH_AMOUNT", "high", 30, "Amount is unusually high for this merchant"),
    "FAILED_PAYMENT": Rule("FAILED_PAYMENT", "medium", 15, "Payment was declined or failed"),
    "IP_REUSE": Rule("IP_REUSE", "high", 25, "IP address is shared by many customers"),
    "DEVICE_REUSE": Rule("DEVICE_REUSE", "critical", 40, "Device is shared by many customers"),
    "VELOCITY": Rule("VELOCITY", "high", 25, "Customer has an unusually high payment velocity"),
    "MODEL_ANOMALY": Rule(
        "MODEL_ANOMALY", "medium", 20, "Payment is anomalous against the observed population"
    ),
}


class RiskEngine:
    """Deterministic, explainable scoring engine with a small unsupervised model."""

    def __init__(self, events: list[PaymentEvent]) -> None:
        self.events = events
        self.merchant_avg: dict[str, float] = defaultdict(float)
        self.ip_customers: dict[str, set[str]] = defaultdict(set)
        self.device_customers: dict[str, set[str]] = defaultdict(set)
        self.customer_counts: dict[str, int] = defaultdict(int)
        for event in events:
            self.merchant_avg[event.merchant_id] += float(event.amount)
            self.ip_customers[event.ip_address].add(event.customer_id)
            self.device_customers[event.device_id].add(event.customer_id)
            self.customer_counts[event.customer_id] += 1
        merchant_counts = defaultdict(int)
        for event in events:
            merchant_counts[event.merchant_id] += 1
        for merchant, total in self.merchant_avg.items():
            self.merchant_avg[merchant] = total / merchant_counts[merchant]
        self.model = self._fit_model()

    def _fit_model(self) -> IsolationForest | None:
        if len(self.events) < 10:
            return None
        values = np.array(
            [[float(e.amount), self.customer_counts[e.customer_id]] for e in self.events]
        )
        model = IsolationForest(random_state=7, contamination="auto", n_estimators=80)
        model.fit(values)
        return model

    def _finding(self, rule: Rule, evidence: dict[str, Any]) -> RiskFinding:
        return RiskFinding(
            rule_id=rule.rule_id,
            severity=rule.severity,
            score=rule.points,
            message=rule.message,
            evidence={key: str(value) for key, value in evidence.items()},
        )

    def assess(self, event: PaymentEvent) -> PaymentRisk:
        findings: list[RiskFinding] = []
        average = self.merchant_avg.get(event.merchant_id, float(event.amount))
        if float(event.amount) > max(average * 3, 500):
            findings.append(
                self._finding(
                    RULES["HIGH_AMOUNT"], {"amount": event.amount, "merchant_avg": average}
                )
            )
        if event.status.value == "failed":
            findings.append(self._finding(RULES["FAILED_PAYMENT"], {"status": event.status.value}))
        if len(self.ip_customers[event.ip_address]) >= 3:
            findings.append(
                self._finding(
                    RULES["IP_REUSE"], {"customers": len(self.ip_customers[event.ip_address])}
                )
            )
        if len(self.device_customers[event.device_id]) >= 3:
            findings.append(
                self._finding(
                    RULES["DEVICE_REUSE"],
                    {"customers": len(self.device_customers[event.device_id])},
                )
            )
        if self.customer_counts[event.customer_id] >= 8:
            findings.append(
                self._finding(
                    RULES["VELOCITY"], {"payments": self.customer_counts[event.customer_id]}
                )
            )
        if self.model is not None:
            features = np.array([[float(event.amount), self.customer_counts[event.customer_id]]])
            if self.model.predict(features)[0] == -1:
                findings.append(
                    self._finding(RULES["MODEL_ANOMALY"], {"model": "isolation_forest"})
                )
        score = min(100.0, sum(f.score for f in findings))
        band = (
            "critical"
            if score >= 75
            else "high"
            if score >= 50
            else "medium"
            if score >= 25
            else "low"
        )
        decision = "block" if score >= 75 else "review" if score >= 40 else "allow"
        return PaymentRisk(
            payment_id=event.payment_id,
            risk_score=score,
            risk_band=band,
            decision=decision,
            findings=findings,
        )

    def assess_all(self) -> dict[str, PaymentRisk]:
        return {event.payment_id: self.assess(event) for event in self.events}
