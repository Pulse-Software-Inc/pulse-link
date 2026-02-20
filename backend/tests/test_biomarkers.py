import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

# check for mock mode
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
USER_TOKEN = os.getenv("FIREBASE_ID_TOKEN", "mock_token" if USE_MOCK else None)

if not USE_MOCK and not os.getenv("FIREBASE_ID_TOKEN"):
    pytest.skip("FIREBASE_ID_TOKEN not set", allow_module_level=True)

headers = {"Authorization": f"Bearer {USER_TOKEN}"}


def test_get_devices():
    response = client.get("/api/v1/biomarkers/devices", headers=headers)
    assert response.status_code == 200
    assert "devices" in response.json()


def test_get_realtime_data():
    response = client.get("/api/v1/biomarkers/real-time", headers=headers)
    assert response.status_code == 200
    assert "data" in response.json()


def test_add_manual_entry():
    entry = {
        "biomarker_type": "weight",
        "value": 72.5,
        "notes": "Test note"
    }
    response = client.post("/api/v1/biomarkers/manual", json=entry, headers=headers)
    assert response.status_code == 200
    assert "entry_id" in response.json()


def test_get_manual_entries():
    response = client.get("/api/v1/biomarkers/manual", headers=headers)
    assert response.status_code == 200
    assert "entries" in response.json()


def test_get_historical_data():
    response = client.get("/api/v1/biomarkers/historical", headers=headers)
    assert response.status_code == 200
