from fastapi.testclient import TestClient

from payinsight.api.app import app

client = TestClient(app)


def test_health_and_metrics():
    assert client.get("/api/health").json()["status"] == "ok"
    body = client.get("/api/metrics").json()
    assert body["total_payments"] == 1000
    assert body["merchants"] > 0


def test_payment_risk_and_list():
    payments = client.get("/api/payments?limit=2")
    assert payments.status_code == 200
    payment_id = payments.json()[0]["payment_id"]
    response = client.get(f"/api/payments/{payment_id}/risk")
    assert response.status_code == 200
    assert "findings" in response.json()
