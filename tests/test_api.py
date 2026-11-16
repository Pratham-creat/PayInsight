from fastapi.testclient import TestClient

from payinsight.api.app import app

client = TestClient(app)

def test_health_and_metrics():
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/metrics").json()["payroll_events"] == 1000

def test_risk_endpoint():
    response = client.get("/employees/E00001/risk")
    assert response.status_code == 200
    assert "findings" in response.json()
