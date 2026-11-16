from datetime import date, datetime
from decimal import Decimal

from payinsight.models import PayrollEvent
from payinsight.risk.rules import evaluate, score


def event(employee, account="a", hours=1):
    return PayrollEvent(employee_id=employee, employer_id="x", pay_date=date.today(),
        gross_pay=Decimal(100), net_pay=Decimal(72), hours=Decimal(hours),
        bank_account_hash=account, created_at=datetime.now())

def test_low_hours_scores_high():
    findings = evaluate([event("E1")])["E1"]
    assert score(findings) == (35.0, "medium")

def test_shared_account_is_critical():
    findings = evaluate([event("E1", "same", 80), event("E2", "same", 80)])
    assert score(findings["E1"])[1] == "high"
