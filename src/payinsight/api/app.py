"""PayInsight HTTP API."""
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from payinsight.models import Metrics, PaymentRisk
from payinsight.pipeline.run import build_demo
from payinsight.pipeline.stages import aggregate_metrics
from payinsight.risk.engine import RiskEngine

app = FastAPI(title="PayInsight", version="1.0.0", description="Payment intelligence API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@lru_cache
def resources():
    warehouse, events = build_demo()
    return warehouse, events, RiskEngine(events)


@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "payinsight"}


@app.get("/api/metrics", response_model=Metrics)
@app.get("/metrics", response_model=Metrics)
def metrics() -> Metrics:
    warehouse, events, engine = resources()
    values = aggregate_metrics(warehouse.query("SELECT * FROM payments"))
    risks = engine.assess_all()
    return Metrics(
        **values,
        high_risk_payments=sum(r.risk_band in ("high", "critical") for r in risks.values()),
    )


@app.get("/api/payments")
def payments(limit: int = Query(50, ge=1, le=500), status: str | None = None) -> list[dict]:
    warehouse, _, _ = resources()
    where = (
        f" WHERE status = '{status}'"
        if status in {"succeeded", "failed", "refunded", "pending"}
        else ""
    )
    return warehouse.query(
        f"SELECT * FROM payments{where} ORDER BY created_at DESC LIMIT {limit}"
    ).to_dicts()


@app.get("/api/payments/{payment_id}/risk", response_model=PaymentRisk)
@app.get("/payments/{payment_id}/risk", response_model=PaymentRisk)
def payment_risk(payment_id: str) -> PaymentRisk:
    _, events, engine = resources()
    event = next((item for item in events if item.payment_id == payment_id), None)
    if event is None:
        raise HTTPException(status_code=404, detail="payment not found")
    return engine.assess(event)


@app.get("/api/merchants/{merchant_id}/summary")
def merchant_summary(merchant_id: str) -> dict:
    warehouse, _, _ = resources()
    frame = warehouse.query(
        "SELECT merchant_id, COUNT(*) AS payments, SUM(amount) AS volume, "
        "AVG(amount) AS average_amount FROM payments "
        f"WHERE merchant_id = '{merchant_id}' GROUP BY merchant_id"
    )
    if frame.is_empty():
        raise HTTPException(status_code=404, detail="merchant not found")
    return frame.to_dicts()[0]
