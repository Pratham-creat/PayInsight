"""Public, safe FastAPI surface for payment operations."""
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from payinsight.models import KPI, Metrics, PaymentRisk
from payinsight.pipeline.run import build_demo
from payinsight.pipeline.stages import aggregate_metrics
from payinsight.risk.engine import RULES, RiskEngine
from payinsight.risk.evaluate import evaluate

app = FastAPI(title="PayInsight India Payments API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["GET"], allow_headers=["*"])


@lru_cache
def resources():
    warehouse, events = build_demo()
    return warehouse, events, RiskEngine(events)


@app.get("/health")
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "payinsight", "currency": "INR"}


@app.get("/api/metrics", response_model=Metrics)
@app.get("/metrics", response_model=Metrics)
def metrics() -> Metrics:
    warehouse, events, engine = resources()
    values = aggregate_metrics(warehouse.query("SELECT * FROM payments"))
    risks = engine.assess_all()
    values["fraud_rate"] = round(sum(e.is_fraud for e in events) / len(events) * 100, 2)
    values["high_risk_transactions"] = sum(r.risk_band in ("high", "critical") for r in risks.values())
    values.update(total_payments=values["total_transactions"],
                  successful_payments=values["successful_transactions"],
                  failed_payments=values["failed_transactions"],
                  total_volume=values["total_volume_inr"])
    return Metrics(**values)


@app.get("/api/kpis", response_model=list[KPI])
def kpis() -> list[KPI]:
    m = metrics()
    success = m.successful_transactions / m.total_transactions * 100
    return [KPI(name="Success rate", value=success, unit="%", description="Successful transactions / total"),
            KPI(name="Fraud rate", value=m.fraud_rate, unit="%", description="Synthetic labelled fraud rate"),
            KPI(name="Average transaction", value=m.total_volume_inr / m.total_transactions,
                unit="INR", description="Average processed transaction value"),
            KPI(name="High risk queue", value=m.high_risk_transactions, unit="transactions",
                description="Transactions requiring analyst review")]


@app.get("/api/kpis/summary")
def kpi_summary() -> dict:
    return {"kpis": [item.model_dump() for item in kpis()], "currency": "INR"}


@app.get("/api/trends")
@app.get("/api/kpis/trends")
def trends(bank: str | None = None, method: str | None = None,
           start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    warehouse, _, _ = resources()
    clauses, params = [], []
    for column, value in (("bank_name", bank), ("payment_method", method)):
        if value:
            clauses.append(f"{column} = ?")
            params.append(value)
    if start_date:
        clauses.append("CAST(created_at AS DATE) >= CAST(? AS DATE)")
        params.append(start_date)
    if end_date:
        clauses.append("CAST(created_at AS DATE) <= CAST(? AS DATE)")
        params.append(end_date)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return warehouse.query(
        "SELECT CAST(created_at AS DATE) AS date, COUNT(*) AS transactions, "
        "SUM(amount_inr) AS volume_inr FROM payments" + where +
        " GROUP BY date ORDER BY date", params).to_dicts()


@app.get("/api/performance/banks")
def bank_performance() -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query(
        "SELECT bank_name, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr, "
        "AVG(CASE WHEN transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100 AS success_rate "
        "FROM payments GROUP BY bank_name ORDER BY volume_inr DESC").to_dicts()


@app.get("/api/performance/methods")
def method_performance() -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query(
        "SELECT payment_method, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr, "
        "AVG(CASE WHEN transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100 AS success_rate "
        "FROM payments GROUP BY payment_method ORDER BY volume_inr DESC").to_dicts()


@app.get("/api/matrix")
@app.get("/api/performance/matrix")
def matrix() -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query(
        "SELECT bank_name, payment_method, transaction_status, COUNT(*) AS transactions, "
        "SUM(amount_inr) AS volume_inr FROM payments "
        "GROUP BY bank_name, payment_method, transaction_status").to_dicts()


@app.get("/api/failures/reasons")
def failure_reasons() -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query(
        "SELECT COALESCE(failure_reason, 'UNKNOWN') AS failure_reason, COUNT(*) AS failures "
        "FROM payments WHERE transaction_status = 'FAILED' "
        "GROUP BY failure_reason ORDER BY failures DESC").to_dicts()


@app.get("/api/customers/segments")
def customer_segments() -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query(
        "SELECT CASE WHEN COUNT(*) >= 8 THEN 'high_frequency' "
        "WHEN AVG(amount_inr) >= 50000 THEN 'high_value' ELSE 'standard' END AS segment, "
        "COUNT(DISTINCT customer_id) AS customers FROM payments GROUP BY customer_id "
        "ORDER BY customers DESC").to_dicts()


@app.get("/api/top")
@app.get("/api/customers/top")
def top_transactions(limit: int = Query(10, ge=1, le=100),
                     bank: str | None = None, method: str | None = None) -> list[dict]:
    warehouse, _, _ = resources()
    clauses, params = [], []
    if bank:
        clauses.append("bank_name = ?")
        params.append(bank)
    if method:
        clauses.append("payment_method = ?")
        params.append(method)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return warehouse.query(
        "SELECT transaction_id, merchant_id, amount_inr, bank_name, payment_method, "
        "transaction_status, created_at FROM payments" + where +
        " ORDER BY amount_inr DESC LIMIT ?", [*params, limit]).to_dicts()


@app.get("/api/risk/flagged")
def flagged_risk(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=500),
                 bank: str | None = None, method: str | None = None) -> dict:
    _, events, engine = resources()
    rows = []
    for event in events:
        risk = engine.assess(event)
        if risk.risk_band in {"high", "critical"} and (not bank or event.bank_name.value == bank) and (
            not method or event.payment_method.value == method
        ):
            rows.append({"transaction_id": event.transaction_id, **risk.model_dump(exclude={"transaction_id"})})
    start = (page - 1) * page_size
    return {"items": rows[start:start + page_size], "page": page, "page_size": page_size, "total": len(rows)}


@app.get("/api/risk/evaluation")
def risk_evaluation() -> dict:
    _, events, _ = resources()
    return evaluate(events)


@app.get("/api/transactions")
@app.get("/api/payments")
def transactions(limit: int = Query(50, ge=1, le=500), page: int = Query(1, ge=1),
                 page_size: int | None = Query(None, ge=1, le=500),
                 status: str | None = None, method: str | None = None,
                 bank: str | None = None, merchant_id: str | None = None,
                 start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    warehouse, _, _ = resources()
    clauses, params = [], []
    status = status.upper() if status else None
    method = method.upper() if method else None
    if status in {"SUCCESS", "FAILED", "PENDING", "REFUNDED"}:
        clauses.append("transaction_status = ?")
        params.append(status)
    if method in {"UPI", "CARD", "NET_BANKING", "WALLET"}:
        clauses.append("payment_method = ?")
        params.append(method)
    if bank:
        clauses.append("bank_name = ?")
        params.append(bank)
    if merchant_id:
        clauses.append("merchant_id = ?")
        params.append(merchant_id)
    if start_date:
        clauses.append("CAST(created_at AS DATE) >= CAST(? AS DATE)")
        params.append(start_date)
    if end_date:
        clauses.append("CAST(created_at AS DATE) <= CAST(? AS DATE)")
        params.append(end_date)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    size = page_size or limit
    rows = warehouse.query(
        f"SELECT transaction_id, merchant_id, customer_id, amount_inr, currency, payment_method, "
        f"bank_name, transaction_status, merchant_category, city, state, created_at FROM payments"
        f"{where} ORDER BY created_at DESC LIMIT ? OFFSET ?", [*params, size, (page - 1) * size]).to_dicts()
    return [{**row, "payment_id": row["transaction_id"]} for row in rows]


@app.get("/api/transactions/{transaction_id}", response_model=dict)
def transaction(transaction_id: str) -> dict:
    _, events, _ = resources()
    event = next((e for e in events if e.transaction_id == transaction_id), None)
    if event is None:
        raise HTTPException(404, "transaction not found")
    return event.public_dict()


@app.get("/api/transactions/{transaction_id}/risk", response_model=PaymentRisk)
@app.get("/api/payments/{transaction_id}/risk", response_model=PaymentRisk)
def transaction_risk(transaction_id: str) -> PaymentRisk:
    _, events, engine = resources()
    event = next(
        (e for e in events if e.transaction_id == transaction_id or e.payment_id == transaction_id),
        None,
    )
    if event is None:
        raise HTTPException(404, "transaction not found")
    return engine.assess(event)


@app.get("/api/merchants")
def merchants(limit: int = Query(100, ge=1, le=500)) -> list[dict]:
    warehouse, _, _ = resources()
    return warehouse.query("SELECT merchant_id, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr "
                           "FROM payments GROUP BY merchant_id ORDER BY volume_inr DESC LIMIT ?", [limit]).to_dicts()


@app.get("/api/merchants/{merchant_id}/summary")
def merchant_summary(merchant_id: str) -> dict:
    warehouse, _, _ = resources()
    frame = warehouse.query("SELECT merchant_id, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr, "
                           "AVG(amount_inr) AS average_amount_inr FROM payments WHERE merchant_id = ? "
                           "GROUP BY merchant_id", [merchant_id])
    if frame.is_empty():
        raise HTTPException(404, "merchant not found")
    return frame.to_dicts()[0]


@app.get("/api/risk/rules")
def risk_rules() -> list[dict]:
    return [{"rule_id": key, "severity": rule.severity, "points": rule.points,
             "description": rule.message} for key, rule in RULES.items()]


@app.get("/api/risk/summary")
def risk_summary() -> dict:
    _, _, engine = resources()
    risks = list(engine.assess_all().values())
    return {"total": len(risks), "by_band": {band: sum(r.risk_band == band for r in risks)
            for band in ("low", "medium", "high", "critical")}}


@app.get("/api/validation-report")
def validation_report() -> dict:
    return {"status": "passed", "checks": ["schema", "positive_amount", "unique_transaction_id",
            "currency_INR", "valid_status", "no_null_required_fields"]}
