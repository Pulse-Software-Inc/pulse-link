from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Any, Dict, List, Tuple
import sys
import os
from datetime import datetime
import firebase_admin.auth as firebase_auth

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, normalize_role, public_role, serialize_public_role_fields
from app.core.dashboard import (
    build_daily_summary,
    build_heart_rate_daily,
    build_last_7_days_metrics,
    build_recent_biomarkers,
    build_weekly_summary,
    get_daily_goals,
    get_dashboard_customization,
    get_emergency_settings,
    serialize_device,
)
from app.models.user import UserUpdate, ConsentSettings, UserSettingsUpdate

router = APIRouter(prefix="/users", tags=["users"])

AVAILABLE_DEVICES = [
    {
        "device_id": "device_fitbit_1",
        "device_name": "Fitbit Sense 2",
        "device_type": "smartwatch",
        "brand": "Fitbit",
        "is_active": False,
        "last_sync": None,
    },
    {
        "device_id": "device_garmin_1",
        "device_name": "Garmin Forerunner",
        "device_type": "smartwatch",
        "brand": "Garmin",
        "is_active": False,
        "last_sync": None,
    },
    {
        "device_id": "device_samsung_1",
        "device_name": "Galaxy Watch 6",
        "device_type": "smartwatch",
        "brand": "Samsung",
        "is_active": False,
        "last_sync": None,
    },
    {
        "device_id": "device_polar_1",
        "device_name": "Polar H10",
        "device_type": "heart_rate_monitor",
        "brand": "Polar",
        "is_active": False,
        "last_sync": None,
    },
    {
        "device_id": "device_oura_1",
        "device_name": "Oura Ring Gen 3",
        "device_type": "ring",
        "brand": "Oura",
        "is_active": False,
        "last_sync": None,
    },
]


def build_provider_profile(user_data: dict) -> dict:
    first_name = (user_data.get("first_name") or "").strip()
    last_name = (user_data.get("last_name") or "").strip()
    name = " ".join(part for part in [first_name, last_name] if part).strip()
    if not name:
        name = (user_data.get("name") or user_data.get("email") or "Provider").strip()
    profile = {
        "email": user_data.get("email"),
        "name": name,
    }
    if "invite_clients" in user_data and user_data.get("invite_clients") is not None:
        profile["invite_clients"] = user_data.get("invite_clients")
    return profile


def sync_provider_profile(firestore_module, user_id: str, user_data: dict):
    if normalize_role(user_data.get("role", "user")) != "healthcare_provider":
        return
    if not firestore_module.upsert_provider_profile(user_id, build_provider_profile(user_data)):
        raise HTTPException(status_code=500, detail="Failed to create provider profile")


def ensure_user_profile(firestore_module, current_user: dict) -> dict:
    user = firestore_module.get_user(current_user["uid"])
    if user:
        return user

    user_data = {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": normalize_role(current_user.get("role", "user")),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    if firestore_module.create_user(current_user["uid"], user_data):
        return user_data
    raise HTTPException(status_code=500, detail="Failed to create user")


def get_name_parts(user: dict) -> Tuple[str, str]:
    first_name = (user.get("first_name") or "").strip()
    last_name = (user.get("last_name") or "").strip()
    if first_name or last_name:
        return first_name, last_name

    full_name = (user.get("name") or "").strip()
    if not full_name:
        return "", ""

    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def sync_settings_devices(firestore_module, user_id: str, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing_devices = firestore_module.get_user_devices(user_id)
    existing_ids = {
        (device.get("device_id") or device.get("id")): device
        for device in existing_devices
        if device.get("device_id") or device.get("id")
    }
    kept_ids = set()

    for device in devices:
        device_payload = {
            "device_name": device["device_name"],
            "device_type": device["device_type"],
            "brand": device.get("brand", ""),
            "is_active": device.get("is_active", True),
        }
        if device.get("last_sync"):
            device_payload["last_sync"] = device["last_sync"]

        device_id = device.get("device_id")
        if device_id and device_id in existing_ids:
            if not firestore_module.update_device(user_id, device_id, device_payload):
                raise HTTPException(status_code=500, detail="Failed to update device")
            kept_ids.add(device_id)
            continue

        created_id = firestore_module.add_device(user_id, device_payload)
        if not created_id:
            raise HTTPException(status_code=500, detail="Failed to save device")
        kept_ids.add(created_id)

    for existing_id in existing_ids:
        if existing_id not in kept_ids:
            firestore_module.delete_device(user_id, existing_id)

    return [serialize_device(device) for device in firestore_module.get_user_devices(user_id)]


@router.get("/me")
async def get_user_profile(request: Request, current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    user = ensure_user_profile(firestore, current_user)

    sync_provider_profile(firestore, current_user["uid"], user)

    return serialize_public_role_fields(user)


@router.put("/me")
async def update_user_profile(request: Request, profile_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    updates = profile_update.model_dump(exclude_unset=True)
    existing_user = firestore.get_user(current_user["uid"])

    if "role" in updates:
        updates["role"] = normalize_role(updates["role"])

    if "email" not in updates or not updates["email"]:
        updates["email"] = current_user["email"]

    if "role" not in updates or not updates["role"]:
        updates["role"] = normalize_role(current_user.get("role", "user"))

    if "email" in updates and updates["email"] and updates["email"] != current_user.get("email"):
        if os.getenv("USE_MOCK", "false").lower() != "true":
            try:
                firebase_auth.update_user(current_user["uid"], email=updates["email"])
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to update auth email: {e}")

    if not existing_user:
        user_data = {
            "uid": current_user["uid"],
            "email": updates["email"],
            "role": updates["role"],
            "created_at": datetime.now().isoformat(),
            **updates,
        }
        created = firestore.create_user(current_user["uid"], user_data)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create user")

        sync_provider_profile(firestore, current_user["uid"], user_data)

        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="update_profile",
            category="general",
            status="success",
            details={"fields": list(updates.keys())},
        )
        return {"message": "Profile updated", "user": serialize_public_role_fields(user_data)}

    updated = firestore.update_user(current_user["uid"], updates)

    if not updated:
        raise HTTPException(status_code=404, detail="Failed to update user")

    firestore.create_audit_log(
        user_id=current_user["uid"],
        action="update_profile",
        category="general",
        status="success",
        details={"fields": list(updates.keys())},
    )

    updated_user = {**existing_user, **updates}
    sync_provider_profile(firestore, current_user["uid"], updated_user)
    return {"message": "Profile updated", "user": serialize_public_role_fields(updated_user)}


@router.get("/dashboard")
async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    user = ensure_user_profile(firestore, current_user)
    sync_provider_profile(firestore, current_user["uid"], user)

    first_name, last_name = get_name_parts(user)
    records = firestore.get_all_biomarkers(current_user["uid"])
    consent = firestore.get_consent_settings(current_user["uid"])
    devices = [serialize_device(device) for device in firestore.get_user_devices(current_user["uid"])]
    public_user = serialize_public_role_fields(user)
    summary = build_daily_summary(records)
    weekly_summary = build_weekly_summary(records)
    heart_rate_daily = build_heart_rate_daily(records)
    biomarkers = build_recent_biomarkers(records, limit=25)

    return {
        "user_id": current_user["uid"],
        "email": user.get("email") or current_user.get("email"),
        "profile": public_user,
        "consent_settings": consent,
        "dashboard_customization": get_dashboard_customization(user),
        "biomarkers": biomarkers,
        "summary": summary,
        "weekly_summary": weekly_summary,
        "heart_rate_daily": heart_rate_daily,
        "devices": devices,
        "fname": first_name,
        "lname": last_name,
        "daily_goals": get_daily_goals(user),
        "metrics_last_7_days": build_last_7_days_metrics(records),
        "ai_instructions": user.get("ai_instructions", "") or "",
    }


@router.get("/settings")
async def get_user_settings(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    user = ensure_user_profile(firestore, current_user)
    sync_provider_profile(firestore, current_user["uid"], user)
    role = normalize_role(user.get("role") or current_user.get("role", "user"))
    provider = firestore.get_provider(current_user["uid"]) if role == "healthcare_provider" else None

    first_name, last_name = get_name_parts(user)

    settings = {
        "fname": first_name,
        "lname": last_name,
        "email": user.get("email") or current_user.get("email"),
        "password": "●●●●●●●●●●",
        "role": public_role(role),
        "language": user.get("language", "en"),
        "ai_instructions": user.get("ai_instructions", "") or "",
    }

    if role == "healthcare_provider":
        settings["invite_clients"] = (provider or {}).get("invite_clients", [])
        return settings

    settings["daily_goals"] = get_daily_goals(user)
    settings["notification_preferences"] = firestore.get_notification_settings(current_user["uid"])
    settings["emergency_settings"] = get_emergency_settings(user)
    settings["devices"] = [serialize_device(device) for device in firestore.get_user_devices(current_user["uid"])]
    settings["available_devices"] = AVAILABLE_DEVICES
    return settings


@router.put("/settings")
async def update_user_settings(settings_update: UserSettingsUpdate, current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    payload = settings_update.model_dump(exclude_unset=True)
    user = ensure_user_profile(firestore, current_user)
    role = normalize_role(user.get("role") or current_user.get("role", "user"))
    user_updates: Dict[str, Any] = {}

    for key in ["first_name", "last_name", "language", "ai_instructions"]:
        if key in payload:
            user_updates[key] = payload[key]

    if role != "healthcare_provider" and "daily_goals" in payload and payload["daily_goals"] is not None:
        user_updates["daily_goals"] = payload["daily_goals"]

    if role != "healthcare_provider" and "emergency_settings" in payload and payload["emergency_settings"] is not None:
        user_updates["emergency_settings"] = payload["emergency_settings"]

    if "email" in payload and payload["email"] and payload["email"] != user.get("email"):
        if os.getenv("USE_MOCK", "false").lower() != "true":
            try:
                firebase_auth.update_user(current_user["uid"], email=payload["email"])
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to update auth email: {e}")
        user_updates["email"] = payload["email"]

    if user_updates:
        if not firestore.update_user(current_user["uid"], user_updates):
            raise HTTPException(status_code=500, detail="Failed to update settings")

    if role != "healthcare_provider" and "notification_preferences" in payload and payload["notification_preferences"] is not None:
        if not firestore.update_notification_settings(current_user["uid"], payload["notification_preferences"]):
            raise HTTPException(status_code=500, detail="Failed to update notification preferences")

    if role != "healthcare_provider" and "devices" in payload and payload["devices"] is not None:
        sync_settings_devices(firestore, current_user["uid"], payload["devices"])

    if role == "healthcare_provider" and "invite_clients" in payload and payload["invite_clients"] is not None:
        sync_provider_profile(
            firestore,
            current_user["uid"],
            {
                **user,
                "invite_clients": payload["invite_clients"],
            },
        )

    updated_user = ensure_user_profile(firestore, current_user)
    sync_provider_profile(firestore, current_user["uid"], updated_user)
    return await get_user_settings(current_user)


@router.post("/settings")
async def post_user_settings(settings_update: UserSettingsUpdate, current_user: dict = Depends(get_current_user)):
    return await update_user_settings(settings_update, current_user)


@router.get("/export/pdf")
async def export_my_pdf(request: Request, current_user: dict = Depends(get_current_user)):
    from app.routers.biomarkers import export_biomarkers

    return await export_biomarkers(request=request, format="pdf", current_user=current_user)


@router.delete("/me")
async def delete_my_account(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    uid = current_user["uid"]
    firestore.create_audit_log(
        user_id=uid,
        action="delete_account",
        category="security",
        status="success",
    )
    deleted = firestore.delete_user_account(uid)

    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete account data")

    if os.getenv("USE_MOCK", "false").lower() != "true":
        try:
            firebase_auth.delete_user(uid)
        except Exception as e:
            print(f"DEBUG: firebase delete failed: {e}")
            raise HTTPException(status_code=500, detail="Firestore data deleted but auth delete failed")

    return {
        "user_id": uid,
        "message": "Account and data deleted"
    }


@router.get("/me/consent")
async def get_consent_settings(request: Request, current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    consent = firestore.get_consent_settings(current_user["uid"])
    return {"user_id": current_user["uid"], "consent": consent}


@router.put("/me/consent")
async def update_consent_settings(request: Request, consent: ConsentSettings, current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    success = firestore.update_consent_settings(current_user["uid"], consent.model_dump())

    if success:
        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="update_consent",
            category="sharing",
            status="success",
            details=consent.model_dump(),
        )
        return {
            "user_id": current_user["uid"],
            "message": "Consent updated",
            "consent": consent
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update consent")


# third party provider linking for google apple and facebook

@router.get("/me/providers")
async def get_linked_providers(current_user: dict = Depends(get_current_user)):
    """get third-party accounts linked to the user"""
    from app.core import firestore
    try:
        uid = current_user["uid"]
        links = firestore.get_provider_links(uid)
        return {"user_id": uid, "linked_providers": links, "count": len(links)}
    except Exception as e:
        print(f"DEBUG: get providers error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch provider links")


@router.post("/me/providers")
async def link_provider_account(payload: dict, current_user: dict = Depends(get_current_user)):
    """store metadata for a linked provider account (oauth handled on client)"""
    from app.core import firestore
    try:
        uid = current_user["uid"]
        provider = (payload.get("provider") or "").lower().strip()
        if provider not in ["google", "apple", "facebook"]:
            raise HTTPException(status_code=400, detail="provider must be google, apple, or facebook")

        link_data = {
            "provider": provider,
            "external_id": payload.get("external_id", ""),
            "email": payload.get("email", current_user.get("email")),
            "linked_at": datetime.now().isoformat(),
            "scopes": payload.get("scopes", []),
        }

        link_id = firestore.add_provider_link(uid, link_data)
        if not link_id:
            raise HTTPException(status_code=500, detail="failed to link provider")

        firestore.create_audit_log(
            user_id=uid,
            action="link_provider",
            category="sharing",
            status="success",
            details={"provider": provider, "link_id": link_id},
        )

        return {"user_id": uid, "link_id": link_id, "message": "provider linked", "provider": provider}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: link provider error: {e}")
        raise HTTPException(status_code=500, detail="failed to link provider")


@router.delete("/me/providers/{link_id}")
async def remove_provider_link(link_id: str, current_user: dict = Depends(get_current_user)):
    """unlink a provider account"""
    from app.core import firestore
    try:
        success = firestore.delete_provider_link(link_id)
        if not success:
            raise HTTPException(status_code=404, detail="link not found")
        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="unlink_provider",
            category="sharing",
            status="success",
            details={"link_id": link_id},
        )
        return {"user_id": current_user["uid"], "link_id": link_id, "message": "provider unlinked"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: delete provider link error: {e}")
        raise HTTPException(status_code=500, detail="failed to unlink provider")


# custom alerts endpoints

@router.get("/me/alerts")
async def get_user_alerts(request: Request, current_user: dict = Depends(get_current_user)):
    """get all custom alert thresholds for the current user"""
    from app.core import firestore

    try:
        uid = current_user["uid"]
        alerts = firestore.get_user_alerts(uid)

        print(f"DEBUG: fetched {len(alerts)} alerts for user {uid}")

        return {
            "user_id": uid,
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        print(f"DEBUG: error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=f"failed to fetch alerts: {e}")


@router.post("/me/alerts")
async def create_alert(
    request: Request,
    alert_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """create a new custom alert threshold"""
    from app.core import firestore

    try:
        uid = current_user["uid"]

        # validate required fields
        required = ["biomarker_type", "condition", "threshold"]
        for field in required:
            if field not in alert_data:
                raise HTTPException(status_code=400, detail=f"missing required field: {field}")

        # validate condition
        valid_conditions = ["greater_than", "less_than", "equals"]
        if alert_data["condition"] not in valid_conditions:
            raise HTTPException(status_code=400, detail=f"invalid condition. must be one of: {valid_conditions}")

        # validate biomarker type
        valid_types = ["heart_rate", "steps", "calories", "sleep_hours", "blood_pressure_systolic", "blood_pressure_diastolic"]
        if alert_data["biomarker_type"] not in valid_types:
            raise HTTPException(status_code=400, detail=f"invalid biomarker_type. must be one of: {valid_types}")

        # set defaults
        alert_data.setdefault("message", f"{alert_data['biomarker_type']} is {alert_data['condition']} {alert_data['threshold']}")
        alert_data.setdefault("enabled", True)

        alert_id = firestore.create_alert(uid, alert_data)

        if not alert_id:
            raise HTTPException(status_code=500, detail="failed to create alert")

        print(f"DEBUG: created alert {alert_id} for user {uid}")

        return {
            "user_id": uid,
            "alert_id": alert_id,
            "message": "alert created successfully",
            "alert": alert_data
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: error creating alert: {e}")
        raise HTTPException(status_code=500, detail=f"failed to create alert: {e}")


@router.delete("/me/alerts/{alert_id}")
async def delete_alert(
    request: Request,
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """delete an alert threshold"""
    from app.core import firestore

    try:
        success = firestore.delete_alert(alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="alert not found")

        print(f"DEBUG: deleted alert {alert_id}")

        return {
            "user_id": current_user["uid"],
            "alert_id": alert_id,
            "message": "alert deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: error deleting alert: {e}")
        raise HTTPException(status_code=500, detail=f"failed to delete alert: {e}")


@router.get("/me/audit-logs")
async def get_my_audit_logs(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    from app.core import firestore

    try:
        logs = firestore.get_audit_logs(current_user["uid"], limit=limit)
        return {
            "user_id": current_user["uid"],
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        print(f"DEBUG: get audit logs error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch audit logs")


@router.get("/me/access-logs")
async def get_my_access_logs(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    from app.core import firestore

    try:
        logs = firestore.get_access_logs(current_user["uid"], limit=limit)
        return {
            "user_id": current_user["uid"],
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        print(f"DEBUG: get access logs error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch access logs")
