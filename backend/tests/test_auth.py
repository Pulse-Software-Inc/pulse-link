import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

USER_TOKEN = os.getenv("FIREBASE_ID_TOKEN")
PROVIDER_TOKEN = os.getenv("FIREBASE_PROVIDER_TOKEN")

if not USER_TOKEN:
    pytest.skip("FIREBASE_ID_TOKEN not set", allow_module_level=True)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_protected_endpoint_without_auth():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403


def test_protected_endpoint_with_user_token():
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()


def test_auth_me_endpoint():
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json().get("uid")


def test_provider_endpoint_with_wrong_role():
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = client.get("/api/v1/providers/patients", headers=headers)
    assert response.status_code in (401, 403)


@pytest.mark.skipif(not PROVIDER_TOKEN, reason="FIREBASE_PROVIDER_TOKEN not set")
def test_provider_endpoint_with_provider_token():
    headers = {"Authorization": f"Bearer {PROVIDER_TOKEN}"}
    response = client.get("/api/v1/providers/patients", headers=headers)
    assert response.status_code == 200
