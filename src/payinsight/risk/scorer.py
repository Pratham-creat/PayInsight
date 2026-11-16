from .engine import RiskEngine


def score_events(events):
    return RiskEngine(events).assess_all()
