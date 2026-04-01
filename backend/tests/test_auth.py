import pytest
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

pytestmark = pytest.mark.anyio

# check for mock mode and skip if using mock
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
USER_TOKEN = os.getenv("FIREBASE_ID_TOKEN", "mock_token" if USE_MOCK else None)
PROVIDER_TOKEN = os.getenv("FIREBASE_PROVIDER_TOKEN", "mock_token" if USE_MOCK else None)

if not USE_MOCK and not os.getenv("FIREBASE_ID_TOKEN"):
    pytest.skip("FIREBASE_ID_TOKEN not set", allow_module_level=True)


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200


async def test_protected_endpoint_without_auth(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code in (401, 403)


async def test_protected_endpoint_with_user_token(client):
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()


async def test_auth_me_endpoint(client):
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json().get("uid")


async def test_provider_endpoint_with_wrong_role(client):
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = await client.get("/api/v1/providers/patients", headers=headers)
    assert response.status_code in (401, 403)


@pytest.mark.skipif(not PROVIDER_TOKEN or USE_MOCK, reason="FIREBASE_PROVIDER_TOKEN not set or using mock mode")
async def test_provider_endpoint_with_provider_token(client):
    headers = {"Authorization": f"Bearer {PROVIDER_TOKEN}"}
    response = await client.get("/api/v1/providers/patients", headers=headers)
    assert response.status_code == 200
