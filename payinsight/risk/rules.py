from collections import defaultdict
from dataclasses import dataclass

from payinsight.models import PayrollEvent, RiskFinding


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    points: float

RULES = (
    Rule("LOW_HOURS", "high", 35),
    Rule("SHARED_BANK_ACCOUNT", "critical", 50),
    Rule("UNUSUAL_PAY_RATIO", "medium", 20),
)

def evaluate(events: list[PayrollEvent]) -> dict[str, list[RiskFinding]]:
    by_account: dict[str, set[str]] = defaultdict(set)
    for e in events:
        by_account[e.bank_account_hash].add(e.employee_id)
    result: dict[str, list[RiskFinding]] = defaultdict(list)
    for e in events:
        if e.hours < 20:
            result[e.employee_id].append(RiskFinding(rule_id="LOW_HOURS", severity="high", score=35,
                message="Pay event has unusually low hours"))
        if len(by_account[e.bank_account_hash]) > 1:
            result[e.employee_id].append(RiskFinding(rule_id="SHARED_BANK_ACCOUNT", severity="critical", score=50,
                message="Bank account is associated with multiple employees"))
        ratio = float(e.net_pay / e.gross_pay) if e.gross_pay else 0
        if ratio < 0.5 or ratio > 0.95:
            result[e.employee_id].append(RiskFinding(rule_id="UNUSUAL_PAY_RATIO", severity="medium", score=20,
                message="Net-to-gross pay ratio is outside expected range"))
    return result

def score(findings: list[RiskFinding]) -> tuple[float, str]:
    value = min(100.0, sum(f.score for f in findings))
    band = "critical" if value >= 75 else "high" if value >= 50 else "medium" if value >= 25 else "low"
    return value, band
