from payinsight.generator.seeded import generate_payments
from payinsight.risk.engine import RiskEngine


def test_risk_engine_returns_explainable_result():
    events = [event for chunk in generate_payments(120) for event in chunk]
    result = RiskEngine(events).assess(events[0])
    assert 0 <= result.risk_score <= 100
    assert result.decision in {"allow", "review", "block"}
    assert all(f.rule_id and f.message for f in result.findings)
