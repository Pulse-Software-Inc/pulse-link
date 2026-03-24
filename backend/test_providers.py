import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_patients(client, monkeypatch):
    # mock auth dependency to simulate provider
    def fake_require_role(role):
        def dep():
            return {"uid": "provider456", "email": "dr.smith@hospital.com", "role": "healthcare_provider"}
        return dep
    
    from app import routers
    routers.providers.require_role = fake_require_role
    
    resp = client.get("/api/v1/providers/patients", headers={"Authorization": "Bearer mock_provider_token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider_id"] == "provider456"
    assert isinstance(data["patients"], list)


def test_set_and_list_alerts(client, monkeypatch):
    def fake_require_role(role):
        def dep():
            return {"uid": "provider456", "email": "dr.smith@hospital.com", "role": "healthcare_provider"}
        return dep
    
    from app import routers
    routers.providers.require_role = fake_require_role
    
    payload = {
        "biomarker_type": "heart_rate",
        "condition": "greater_than",
        "threshold": 120,
        "message": "high hr"
    }
    create = client.post("/api/v1/providers/alerts?patient_id=user123", json=payload, headers={"Authorization": "Bearer mock_provider_token"})
    assert create.status_code == 200
    created = create.json()
    assert created.get("alert_id")
    
    listing = client.get("/api/v1/providers/alerts", headers={"Authorization": "Bearer mock_provider_token"})
    assert listing.status_code == 200
    alerts = listing.json().get("alerts", [])
    assert any(a.get("patient_id") == "user123" for a in alerts)
