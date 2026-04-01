import os
import sys
from copy import deepcopy
import time

import pytest
import httpx

os.environ["USE_MOCK"] = "true"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.core.mock_db import mock_db
from app.core.security import get_current_user
from app.routers.biomarkers import REPORTLAB_AVAILABLE

pytestmark = pytest.mark.anyio

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def reset_mock_state():
    names = [
        "users",
        "devices",
        "biomarkers",
        "providers",
        "consent",
        "manual_entries",
        "linked_providers",
        "social_shares",
        "appointments",
        "support_tickets",
        "patient_alerts",
        "notifications",
        "alerts",
        "emergency_contacts",
        "mfa_state",
        "audit_logs",
    ]
    old_state = {name: deepcopy(getattr(mock_db, name)) for name in names}
    yield
    for name, value in old_state.items():
        setattr(mock_db, name, value)
    app.dependency_overrides.clear()


async def test_device_management_flow(client):
    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
        }

    app.dependency_overrides[get_current_user] = user_override

    create_resp = await client.post(
        "/api/v1/biomarkers/devices",
        json={
            "device_name": "Test Band",
            "device_type": "fitness_tracker",
            "brand": "Demo",
        },
    )
    assert create_resp.status_code == 200
    device_id = create_resp.json()["device_id"]

    update_resp = await client.put(
        f"/api/v1/biomarkers/devices/{device_id}",
        json={"is_active": False},
    )
    assert update_resp.status_code == 200

    delete_resp = await client.delete(f"/api/v1/biomarkers/devices/{device_id}")
    assert delete_resp.status_code == 200


async def test_mfa_request_and_verify_flow(client):
    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
        }

    app.dependency_overrides[get_current_user] = user_override

    request_resp = await client.post("/api/v1/auth/mfa/request")
    assert request_resp.status_code == 200
    code = request_resp.json()["code"]

    verify_resp = await client.post("/api/v1/auth/mfa/verify", json={"code": code})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True

    status_resp = await client.get("/api/v1/auth/mfa/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["mfa"]["verified"] is True


async def test_change_password_rejects_weak_password(client):
    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
        }

    app.dependency_overrides[get_current_user] = user_override

    resp = await client.post("/api/v1/auth/change-password?new_password=weak")
    assert resp.status_code == 400
    assert "password" in resp.json()["detail"]


async def test_provider_patient_data_with_consent(client):
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

    resp = await client.get("/api/v1/providers/patients/user123/data")
    assert resp.status_code == 200
    data = resp.json()
    assert data["patient"]["uid"] == "user123"
    assert "summary" in data
    assert "recent_biomarkers" in data


async def test_notification_preferences_can_disable_provider_alerts(client):
    mock_db.consent["user123"] = {
        "share_with_healthcare_providers": True,
        "share_anonymized_data": False,
        "data_retention_days": 7,
    }

    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
        }

    app.dependency_overrides[get_current_user] = user_override
    pref_resp = await client.put(
        "/api/v1/notifications/preferences",
        json={"provider_alert": False},
    )
    assert pref_resp.status_code == 200
    assert pref_resp.json()["preferences"]["provider_alert"] is False

    async def provider_override():
        return {
            "uid": "provider456",
            "email": "dr.smith@hospital.com",
            "role": "healthcare_provider",
            "mfa_verified": True,
        }

    app.dependency_overrides[get_current_user] = provider_override
    alert_resp = await client.post(
        "/api/v1/providers/alerts?patient_id=user123",
        json={
            "biomarker_type": "heart_rate",
            "condition": "greater_than",
            "threshold": 120,
            "message": "provider warning"
        },
    )
    assert alert_resp.status_code == 200
    assert mock_db.notifications.get("user123", []) == []


async def test_access_logs_show_provider_data_access(client):
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
            "password_expired": False,
        }

    app.dependency_overrides[get_current_user] = provider_override
    provider_resp = await client.get("/api/v1/providers/patients/user123/data")
    assert provider_resp.status_code == 200

    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
            "password_expired": False,
        }

    app.dependency_overrides[get_current_user] = user_override
    logs_resp = await client.get("/api/v1/users/me/access-logs")
    assert logs_resp.status_code == 200
    assert logs_resp.json()["count"] >= 1


async def test_session_cookie_login_flow(client, monkeypatch):
    from app.routers import auth as auth_router
    from app.core import security as security_module

    def fake_verify_id_token(token, check_revoked=True):
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "auth_time": int(time.time()),
        }

    def fake_create_session_cookie(id_token, expires_in):
        return "fake_session_cookie"

    def fake_verify_session_cookie(cookie, check_revoked=True):
        if cookie != "fake_session_cookie":
            raise ValueError("bad cookie")
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
        }

    monkeypatch.setattr(auth_router.firebase_auth, "verify_id_token", fake_verify_id_token)
    monkeypatch.setattr(auth_router.firebase_auth, "create_session_cookie", fake_create_session_cookie)
    monkeypatch.setattr(security_module.firebase_auth, "verify_session_cookie", fake_verify_session_cookie)

    csrf_resp = await client.get("/api/v1/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.json()["csrf_token"]

    login_resp = await client.post(
        "/api/v1/auth/session-login",
        json={"id_token": "fake_id_token", "csrf_token": csrf_token},
    )
    assert login_resp.status_code == 200

    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["uid"] == "user123"


async def test_backup_route_creates_file(client, tmp_path):
    os.environ["PULSELINK_BACKUP_DIR"] = str(tmp_path)

    async def provider_override():
        return {
            "uid": "provider456",
            "email": "dr.smith@hospital.com",
            "role": "healthcare_provider",
            "mfa_verified": True,
            "password_expired": False,
        }

    app.dependency_overrides[get_current_user] = provider_override
    resp = await client.post("/api/v1/support/backups/run")
    assert resp.status_code == 200
    backup_path = resp.json()["backup"]["path"]
    assert os.path.exists(backup_path)


async def test_delete_account_removes_user_data(client):
    temp_uid = "temp_delete_user"
    mock_db.users[temp_uid] = {
        "uid": temp_uid,
        "email": "temp@example.com",
        "role": "user",
    }
    mock_db.devices[temp_uid] = [
        {"device_id": "temp_device", "device_name": "Temp Watch", "device_type": "smartwatch"}
    ]
    mock_db.consent[temp_uid] = {
        "share_with_healthcare_providers": True,
        "share_anonymized_data": False,
        "data_retention_days": 7,
    }

    async def delete_user_override():
        return {
            "uid": temp_uid,
            "email": "temp@example.com",
            "role": "user",
            "mfa_verified": True,
        }

    app.dependency_overrides[get_current_user] = delete_user_override

    resp = await client.delete("/api/v1/users/me")
    assert resp.status_code == 200
    assert temp_uid not in mock_db.users
    assert temp_uid not in mock_db.devices
    assert temp_uid not in mock_db.consent


async def test_user_pdf_export(client):
    if not REPORTLAB_AVAILABLE:
        pytest.skip("reportlab not installed")

    async def user_override():
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "mfa_verified": False,
        }

    app.dependency_overrides[get_current_user] = user_override

    resp = await client.get("/api/v1/biomarkers/export?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/pdf")
