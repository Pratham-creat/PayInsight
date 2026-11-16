from fastapi import FastAPI, HTTPException

from payinsight.generator.seeded import generate_events
from payinsight.models import EmployeeRisk
from payinsight.risk.rules import evaluate, score

app = FastAPI(title="PayInsight API", version="0.1.0")
_events = [event for chunk in generate_events(1000) for event in chunk]
_findings = evaluate(_events)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/metrics")
@app.get("/api/metrics")
def metrics() -> dict:
    return {"payroll_events": len(_events), "employees": len({e.employee_id for e in _events})}

@app.get("/employees/{employee_id}/risk", response_model=EmployeeRisk)
@app.get("/api/employees/{employee_id}/risk", response_model=EmployeeRisk)
def employee_risk(employee_id: str) -> EmployeeRisk:
    if employee_id not in {e.employee_id for e in _events}:
        raise HTTPException(404, "employee not found")
    findings = _findings.get(employee_id, [])
    value, band = score(findings)
    return EmployeeRisk(employee_id=employee_id, score=value, band=band, findings=findings)
