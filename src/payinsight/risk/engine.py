"""Explainable Indian payment risk rules and model signal."""
from collections import defaultdict
from dataclasses import dataclass

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
    "HIGH_VALUE": Rule("HIGH_VALUE", "high", 30, "Amount is unusually high"),
    "FAILED_TRANSACTION": Rule("FAILED_TRANSACTION", "medium", 15, "Transaction failed"),
    "SHARED_IP": Rule("SHARED_IP", "high", 25, "IP is shared by multiple customers"),
    "SHARED_DEVICE": Rule("SHARED_DEVICE", "critical", 40, "Device is shared by multiple customers"),
    "VELOCITY": Rule("VELOCITY", "high", 25, "Customer has unusually high velocity"),
    "MODEL_ANOMALY": Rule("MODEL_ANOMALY", "medium", 20, "Model detected an unusual transaction"),
}


class RiskEngine:
    def __init__(self, events: list[PaymentEvent]):
        self.events = events
        self.avg = defaultdict(float)
        counts = defaultdict(int)
        self.ips, self.devices, self.customers = defaultdict(set), defaultdict(set), defaultdict(int)
        for event in events:
            self.avg[event.merchant_id] += float(event.amount_inr)
            counts[event.merchant_id] += 1
            self.ips[event.ip_address].add(event.customer_id)
            self.devices[event.device_id].add(event.customer_id)
            self.customers[event.customer_id] += 1
        for key in self.avg:
            self.avg[key] /= counts[key]
        self.model = None
        if len(events) >= 10:
            values = np.array([[float(e.amount_inr), self.customers[e.customer_id]] for e in events])
            self.model = IsolationForest(random_state=7, n_estimators=80).fit(values)

    def assess(self, event: PaymentEvent) -> PaymentRisk:
        findings = []
        def add(rule_id: str, evidence: dict):
            rule = RULES[rule_id]
            findings.append(RiskFinding(rule_id=rule.rule_id, severity=rule.severity,
                                        score=rule.points, message=rule.message,
                                        evidence={k: str(v) for k, v in evidence.items()}))
        if float(event.amount_inr) > max(self.avg[event.merchant_id] * 3, 100000):
            add("HIGH_VALUE", {"amount_inr": event.amount_inr})
        if event.transaction_status.value == "FAILED":
            add("FAILED_TRANSACTION", {"status": event.transaction_status.value})
        if len(self.ips[event.ip_address]) >= 3:
            add("SHARED_IP", {"customers": len(self.ips[event.ip_address])})
        if len(self.devices[event.device_id]) >= 3:
            add("SHARED_DEVICE", {"customers": len(self.devices[event.device_id])})
        if self.customers[event.customer_id] >= 8:
            add("VELOCITY", {"transactions": self.customers[event.customer_id]})
        if self.model is not None and self.model.predict(
            np.array([[float(event.amount_inr), self.customers[event.customer_id]]])
        )[0] == -1:
            add("MODEL_ANOMALY", {"model": "isolation_forest"})
        score = min(100.0, sum(f.score for f in findings))
        band = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
        decision = "block" if score >= 75 else "review" if score >= 40 else "allow"
        return PaymentRisk(transaction_id=event.transaction_id, risk_score=score,
                          risk_band=band, decision=decision, findings=findings)

    def assess_all(self) -> dict[str, PaymentRisk]:
        return {event.transaction_id: self.assess(event) for event in self.events}
