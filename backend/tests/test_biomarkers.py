import pytest
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

pytestmark = pytest.mark.anyio

# check for mock mode
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
USER_TOKEN = os.getenv("FIREBASE_ID_TOKEN", "mock_token" if USE_MOCK else None)

if not USE_MOCK and not os.getenv("FIREBASE_ID_TOKEN"):
    pytest.skip("FIREBASE_ID_TOKEN not set", allow_module_level=True)

headers = {"Authorization": f"Bearer {USER_TOKEN}"}


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_get_devices(client):
    response = await client.get("/api/v1/biomarkers/devices", headers=headers)
    assert response.status_code == 200
    assert "devices" in response.json()


async def test_get_realtime_data(client):
    response = await client.get("/api/v1/biomarkers/real-time", headers=headers)
    assert response.status_code == 200
    assert "data" in response.json()


async def test_add_manual_entry(client):
    entry = {
        "biomarker_type": "weight",
        "value": 72.5,
        "notes": "Test note"
    }
    response = await client.post("/api/v1/biomarkers/manual", json=entry, headers=headers)
    assert response.status_code == 200
    assert "entry_id" in response.json()


async def test_get_manual_entries(client):
    response = await client.get("/api/v1/biomarkers/manual", headers=headers)
    assert response.status_code == 200
    assert "entries" in response.json()


async def test_get_historical_data(client):
    response = await client.get("/api/v1/biomarkers/historical", headers=headers)
    assert response.status_code == 200
