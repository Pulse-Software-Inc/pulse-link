import pytest
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import app
from app.core.mock_db import mock_db
from app.core.security import get_current_user

pytestmark = pytest.mark.anyio

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def cleanup_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


async def test_get_patients(client):
    mock_db.consent["user123"] = {
        "share_with_healthcare_providers": True,
        "share_anonymized_data": False,
        "data_retention_days": 7,
    }

    async def provider_override():
        return {
            "uid": "provider456",
            "email": "dr.smith@hospital.com",
            "role": "healthcare_provider",
            "mfa_verified": True,
        }

    app.dependency_overrides[get_current_user] = provider_override

    resp = await client.get("/api/v1/providers/patients", headers={"Authorization": "Bearer mock_provider_token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider_id"] == "provider456"
    assert isinstance(data["patients"], list)


async def test_set_and_list_alerts(client):
    mock_db.consent["user123"] = {
        "share_with_healthcare_providers": True,
        "share_anonymized_data": False,
        "data_retention_days": 7,
    }

    async def provider_override():
        return {
            "uid": "provider456",
            "email": "dr.smith@hospital.com",
            "role": "healthcare_provider",
            "mfa_verified": True,
        }

    app.dependency_overrides[get_current_user] = provider_override

    payload = {
        "biomarker_type": "heart_rate",
        "condition": "greater_than",
        "threshold": 120,
        "message": "high hr"
    }
    create = await client.post("/api/v1/providers/alerts?patient_id=user123", json=payload, headers={"Authorization": "Bearer mock_provider_token"})
    assert create.status_code == 200
    created = create.json()
    assert created.get("alert_id")
    assert len(mock_db.notifications.get("user123", [])) == 1
    assert mock_db.notifications["user123"][0]["type"] == "provider_alert"
    
    listing = await client.get("/api/v1/providers/alerts", headers={"Authorization": "Bearer mock_provider_token"})
    assert listing.status_code == 200
    alerts = listing.json().get("alerts", [])
    assert any(a.get("patient_id") == "user123" for a in alerts)
