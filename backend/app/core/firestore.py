from firebase_admin import firestore as fs
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import os

_db = None
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
PASSWORD_EXPIRY_DAYS = int(os.getenv("PASSWORD_EXPIRY_DAYS", "90"))

def get_db():
    global _db
    if _db is None:
        _db = fs.client()
    return _db


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def get_user(uid: str) -> Optional[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_user(uid)
    client = get_db()
    try:
        doc = client.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Failed to get user: {e}")
        return None


def update_user(uid: str, data: Dict[str, Any]) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.update_user(uid, data)
    try:
        db = get_db()
        data["updated_at"] = datetime.now().isoformat()
        db.collection("users").document(uid).set(data, merge=True)
        return True
    except Exception:
        # forgot to add error message here
        return False


def create_user(uid: str, user_data: Dict[str, Any]) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        now = datetime.now().isoformat()
        if "created_at" not in user_data:
            user_data["created_at"] = now
        if "password_updated_at" not in user_data:
            user_data["password_updated_at"] = now
        if "password_expires_at" not in user_data:
            user_data["password_expires_at"] = (datetime.now() + timedelta(days=PASSWORD_EXPIRY_DAYS)).isoformat()
        user_data["updated_at"] = now
        mock_db.users[uid] = user_data
        return True
    db = get_db()
    try:
        now = datetime.now().isoformat()
        if "created_at" not in user_data:
            user_data["created_at"] = now
        if "password_updated_at" not in user_data:
            user_data["password_updated_at"] = now
        if "password_expires_at" not in user_data:
            user_data["password_expires_at"] = (datetime.now() + timedelta(days=PASSWORD_EXPIRY_DAYS)).isoformat()
        user_data["updated_at"] = now
        db.collection("users").document(uid).set(user_data)
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_user_devices(user_id)
    try:
        db = get_db()
        docs = db.collection("devices").where("user_id", "==", user_id).get()
        # debug
        print(f"Found {len(docs)} devices for user {user_id}")
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)
        return result
    except Exception as e:
        print(f"Device query failed: {e}")
        return []


def add_device(user_id: str, device_data: Dict[str, Any]) -> str:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_device(user_id, device_data)
    db = get_db()
    try:
        now = datetime.now().isoformat()
        device_data["user_id"] = user_id
        device_data["created_at"] = now
        device_data["updated_at"] = now
        
        ref = db.collection("devices").add(device_data)
        device_id = ref[1].id
        
        # update with the id we got
        device_data["device_id"] = device_id
        db.collection("devices").document(device_id).set(device_data)
        
        return device_id
    except Exception as e:
        print(f"Error adding device: {e}")
        return ""


def update_device(user_id: str, device_id: str, updates: Dict[str, Any]) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.update_device(user_id, device_id, updates)
    try:
        db = get_db()
        doc = db.collection("devices").document(device_id).get()
        if not doc.exists:
            return False
        data = doc.to_dict() or {}
        if data.get("user_id") != user_id:
            return False
        updates["updated_at"] = datetime.now().isoformat()
        db.collection("devices").document(device_id).update(updates)
        return True
    except Exception as e:
        print(f"Error updating device: {e}")
        return False


def delete_device(user_id: str, device_id: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.delete_device(user_id, device_id)
    try:
        db = get_db()
        doc = db.collection("devices").document(device_id).get()
        if not doc.exists:
            return False
        data = doc.to_dict() or {}
        if data.get("user_id") != user_id:
            return False
        db.collection("devices").document(device_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting device: {e}")
        return False


def get_manual_entries(user_id: str) -> List[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_manual_entries(user_id)
    try:
        db = get_db()
        docs = db.collection("manual_entries").where("user_id", "==", user_id).get()
        return [doc_to_dict(doc) for doc in docs]
    except:
        return []


def add_manual_entry(user_id: str, entry_data: Dict[str, Any]) -> str:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_manual_entry(user_id, entry_data)
    db = get_db()
    try:
        entry_data["user_id"] = user_id
        if "timestamp" not in entry_data:
            entry_data["timestamp"] = datetime.now().isoformat()
        
        # add the doc
        ref = db.collection("manual_entries").add(entry_data)
        entry_id = ref[1].id
        
        # update with entry_id
        entry_data["entry_id"] = entry_id
        db.collection("manual_entries").document(entry_id).set(entry_data)
        
        return entry_id
    except Exception as e:
        print(f"Failed to add manual entry: {e}")
        return ""


def delete_manual_entry(entry_id: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        for user_id, entries in mock_db.manual_entries.items():
            for i, entry in enumerate(entries):
                if entry.get("entry_id") == entry_id:
                    entries.pop(i)
                    return True
        return False
    try:
        client = get_db()
        client.collection("manual_entries").document(entry_id).delete()
        return True
    except Exception as e:
        print(f"Delete failed for {entry_id}: {e}")
        return False


def get_recent_biomarkers(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_real_time_data(user_id)
    try:
        db = get_db()
        docs = db.collection("biomarkers").where("user_id", "==", user_id).limit(limit).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"Error getting biomarkers: {e}")
        return []


def get_all_biomarkers(user_id: str) -> List[Dict[str, Any]]:
    # get all biomarkers for a user (for export)
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.biomarkers.get(user_id, [])
    try:
        db = get_db()
        docs = db.collection("biomarkers").where("user_id", "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"Error getting all biomarkers: {e}")
        return []


def get_consent_settings(user_id: str) -> Dict[str, Any]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if user_id in mock_db.consent:
            return mock_db.consent[user_id]
        return {
            "share_with_healthcare_providers": False,
            "share_anonymized_data": False,
            "data_retention_days": 7,
        }
    db = get_db()
    try:
        doc = db.collection("consent").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        # return defaults
        return {
            "share_with_healthcare_providers": False,
            "share_anonymized_data": False,
            "data_retention_days": 7,
        }
    except:
        # return empty if error
        return {}


def update_consent_settings(user_id: str, settings: Dict[str, Any]) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        mock_db.consent[user_id] = settings
        return True
    try:
        db = get_db()
        db.collection("consent").document(user_id).set(settings)
        return True
    except Exception as e:
        print(f"Consent update failed: {e}")
        return False


def save_mfa_code(user_id: str, code: str, expires_at: str, delivery_method: str = "in_app") -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.save_mfa_code(user_id, code, expires_at)
    try:
        db = get_db()
        db.collection("mfa_state").document(user_id).set({
            "code_hash": hash_text(code),
            "expires_at": expires_at,
            "verified": False,
            "verified_at": None,
            "verified_until": None,
            "delivery_method": delivery_method,
        })
        return True
    except Exception as e:
        print(f"MFA save failed: {e}")
        return False


def verify_mfa_code(user_id: str, code: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        verified_until = (datetime.now() + timedelta(hours=12)).isoformat()
        return mock_db.verify_mfa_code(user_id, code, verified_until)
    try:
        db = get_db()
        doc = db.collection("mfa_state").document(user_id).get()
        if not doc.exists:
            return False
        state = doc.to_dict() or {}
        if state.get("code_hash") != hash_text(code):
            return False
        expires_at = state.get("expires_at")
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at)
            if expires_dt < datetime.now():
                return False
        verified_until = (datetime.now() + timedelta(hours=12)).isoformat()
        db.collection("mfa_state").document(user_id).set({
            "verified": True,
            "verified_at": datetime.now().isoformat(),
            "verified_until": verified_until,
        }, merge=True)
        return True
    except Exception as e:
        print(f"MFA verify failed: {e}")
        return False


def get_mfa_status(user_id: str) -> Dict[str, Any]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_mfa_status(user_id)
    try:
        db = get_db()
        doc = db.collection("mfa_state").document(user_id).get()
        if not doc.exists:
            return {
                "verified": False,
                "verified_until": None,
                "expires_at": None,
                "has_pending_code": False,
            }
        state = doc.to_dict() or {}
        verified = False
        verified_until = state.get("verified_until")
        if verified_until:
            try:
                verified = datetime.fromisoformat(verified_until) > datetime.now()
            except Exception:
                verified = False
        has_pending_code = bool(state.get("code")) and not verified
        return {
            "verified": verified,
            "verified_until": verified_until,
            "expires_at": state.get("expires_at"),
            "delivery_method": state.get("delivery_method", "in_app"),
            "has_pending_code": bool(state.get("code_hash")) and not verified,
        }
    except Exception as e:
        print(f"MFA status failed: {e}")
        return {
            "verified": False,
            "verified_until": None,
            "expires_at": None,
            "delivery_method": "in_app",
            "has_pending_code": False,
        }


def clear_mfa_state(user_id: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.clear_mfa_state(user_id)
    try:
        db = get_db()
        db.collection("mfa_state").document(user_id).delete()
        return True
    except Exception as e:
        print(f"MFA clear failed: {e}")
        return False


def create_audit_log(
    user_id: Optional[str],
    action: str,
    category: str = "general",
    target_user_id: Optional[str] = None,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
) -> str:
    log_data = {
        "user_id": user_id,
        "target_user_id": target_user_id,
        "action": action,
        "category": category,
        "status": status,
        "details": details or {},
        "created_at": datetime.now().isoformat(),
    }

    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_audit_log(log_data)

    try:
        db = get_db()
        ref = db.collection("audit_logs").add(log_data)
        audit_id = ref[1].id
        db.collection("audit_logs").document(audit_id).set({"audit_id": audit_id}, merge=True)
        return audit_id
    except Exception as e:
        print(f"DEBUG: create audit log error: {e}")
        return ""


def get_audit_logs(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_audit_logs(user_id, limit=limit)

    try:
        db = get_db()
        rows = {}
        for field_name in ["user_id", "target_user_id"]:
            docs = db.collection("audit_logs").where(field_name, "==", user_id).get()
            for doc in docs:
                data = doc_to_dict(doc)
                rows[data["id"]] = data
        logs = list(rows.values())
        logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return logs[:limit]
    except Exception as e:
        print(f"DEBUG: get audit logs error: {e}")
        return []


def get_access_logs(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    logs = get_audit_logs(user_id, limit=limit * 2)
    filtered = [
        log for log in logs
        if log.get("category") in ["data_access", "sharing"]
    ]
    return filtered[:limit]


def get_password_status(user_id: str) -> Dict[str, Any]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_password_status(user_id)

    user = get_user(user_id) or {}
    updated_at = user.get("password_updated_at") or user.get("created_at")
    expires_at = user.get("password_expires_at")

    if not expires_at and updated_at:
        try:
            expires_at = (datetime.fromisoformat(updated_at) + timedelta(days=PASSWORD_EXPIRY_DAYS)).isoformat()
        except Exception:
            expires_at = None

    expired = False
    if expires_at:
        try:
            expired = datetime.fromisoformat(expires_at) < datetime.now()
        except Exception:
            expired = False

    return {
        "password_updated_at": updated_at,
        "password_expires_at": expires_at,
        "expired": expired,
    }


def mark_password_changed(user_id: str, days_until_expiry: int = PASSWORD_EXPIRY_DAYS) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.mark_password_changed(user_id, days_until_expiry)

    user = get_user(user_id)
    if not user:
        return False

    now = datetime.now().isoformat()
    return update_user(user_id, {
        "password_updated_at": now,
        "password_expires_at": (datetime.now() + timedelta(days=days_until_expiry)).isoformat(),
    })


def doc_to_dict(doc):
    """convert doc to dict with id"""
    d = doc.to_dict()
    d["id"] = doc.id
    return d


# custom alerts functions

def get_user_alerts(user_id: str) -> List[Dict[str, Any]]:
    """get all alert thresholds for a user"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return getattr(mock_db, 'alerts', {}).get(user_id, [])
    try:
        db = get_db()
        docs = db.collection("alerts").where("user_id", "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: error getting alerts: {e}")
        return []


def create_alert(user_id: str, alert_data: Dict[str, Any]) -> str:
    """create a new alert threshold"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if not hasattr(mock_db, 'alerts'):
            mock_db.alerts = {}
        if user_id not in mock_db.alerts:
            mock_db.alerts[user_id] = []
        alert_id = f"alert_{len(mock_db.alerts[user_id]) + 1}"
        alert_data["alert_id"] = alert_id
        alert_data["user_id"] = user_id
        alert_data["created_at"] = datetime.now().isoformat()
        mock_db.alerts[user_id].append(alert_data)
        return alert_id
    
    db = get_db()
    try:
        alert_data["user_id"] = user_id
        alert_data["created_at"] = datetime.now().isoformat()
        alert_data["enabled"] = alert_data.get("enabled", True)
        
        ref = db.collection("alerts").add(alert_data)
        alert_id = ref[1].id
        
        # update with the id
        alert_data["alert_id"] = alert_id
        db.collection("alerts").document(alert_id).set(alert_data)
        
        return alert_id
    except Exception as e:
        print(f"DEBUG: create alert failed: {e}")
        return ""


def delete_alert(alert_id: str) -> bool:
    """delete an alert by id"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'alerts'):
            for user_id, alerts in mock_db.alerts.items():
                for i, alert in enumerate(alerts):
                    if alert.get("alert_id") == alert_id:
                        mock_db.alerts[user_id].pop(i)
                        return True
        return False
    
    try:
        db = get_db()
        db.collection("alerts").document(alert_id).delete()
        return True
    except Exception as e:
        print(f"DEBUG: delete alert failed: {e}")
        return False


def update_alert(alert_id: str, alert_data: Dict[str, Any]) -> bool:
    """update an existing alert"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'alerts'):
            for user_id, alerts in mock_db.alerts.items():
                for alert in alerts:
                    if alert.get("alert_id") == alert_id:
                        alert.update(alert_data)
                        alert["updated_at"] = datetime.now().isoformat()
                        return True
        return False
    
    try:
        db = get_db()
        alert_data["updated_at"] = datetime.now().isoformat()
        db.collection("alerts").document(alert_id).update(alert_data)
        return True
    except Exception as e:
        print(f"DEBUG: update alert failed: {e}")
        return False


# notification functions

def get_user_notifications(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """get notifications for a user, sorted by date"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if not hasattr(mock_db, 'notifications'):
            mock_db.notifications = {}
        notifs = mock_db.notifications.get(user_id, [])
        # sort by created_at desc
        notifs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return notifs[:limit]
    
    try:
        db = get_db()
        docs = db.collection("notifications").where("user_id", "==", user_id).get()
        notifications = [doc_to_dict(d) for d in docs]
        notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return notifications[:limit]
    except Exception as e:
        print(f"DEBUG: get notifications error: {e}")
        return []


def create_notification(notification_data: Dict[str, Any]) -> str:
    """create a new notification"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if not hasattr(mock_db, 'notifications'):
            mock_db.notifications = {}
        user_id = notification_data.get("user_id")
        if user_id not in mock_db.notifications:
            mock_db.notifications[user_id] = []
        notif_id = f"notif_{len(mock_db.notifications[user_id]) + 1}"
        notification_data["id"] = notif_id
        mock_db.notifications[user_id].append(notification_data)
        return notif_id
    
    try:
        db = get_db()
        ref = db.collection("notifications").add(notification_data)
        return ref[1].id
    except Exception as e:
        print(f"DEBUG: create notification error: {e}")
        return ""


def get_notification_settings(user_id: str) -> Dict[str, Any]:
    defaults = {
        "mute_all": False,
        "general": True,
        "appointment": True,
        "provider_alert": True,
        "emergency": True,
        "companion": True,
        "daily_summary": True,
        "health_alert": True,
        "quiet_hours_start": "",
        "quiet_hours_end": "",
    }

    user = get_user(user_id) or {}
    settings = user.get("notification_settings", {})

    merged = defaults.copy()
    merged.update(settings)
    return merged


def update_notification_settings(user_id: str, settings: Dict[str, Any]) -> bool:
    current = get_notification_settings(user_id)
    current.update(settings)

    user = get_user(user_id)
    if not user:
        return create_user(user_id, {
            "uid": user_id,
            "notification_settings": current,
        })

    return update_user(user_id, {"notification_settings": current})


def mark_notification_read(notification_id: str) -> bool:
    """mark a single notification as read"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'notifications'):
            for user_id, notifs in mock_db.notifications.items():
                for n in notifs:
                    if n.get("id") == notification_id or n.get("notification_id") == notification_id:
                        n["read"] = True
                        return True
        return False
    
    try:
        db = get_db()
        db.collection("notifications").document(notification_id).update({"read": True})
        return True
    except Exception as e:
        print(f"DEBUG: mark notification read error: {e}")
        return False


def mark_all_notifications_read(user_id: str) -> int:
    """mark all notifications for a user as read"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        count = 0
        if hasattr(mock_db, 'notifications') and user_id in mock_db.notifications:
            for n in mock_db.notifications[user_id]:
                if not n.get("read", False):
                    n["read"] = True
                    count += 1
        return count
    
    try:
        db = get_db()
        docs = db.collection("notifications").where("user_id", "==", user_id).where("read", "==", False).get()
        count = 0
        for doc in docs:
            doc.reference.update({"read": True})
            count += 1
        return count
    except Exception as e:
        print(f"DEBUG: mark all read error: {e}")
        return 0


def delete_notification(notification_id: str) -> bool:
    """delete a notification"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'notifications'):
            for user_id, notifs in mock_db.notifications.items():
                for i, n in enumerate(notifs):
                    if n.get("id") == notification_id or n.get("notification_id") == notification_id:
                        notifs.pop(i)
                        return True
        return False
    
    try:
        db = get_db()
        db.collection("notifications").document(notification_id).delete()
        return True
    except Exception as e:
        print(f"DEBUG: delete notification error: {e}")
        return False


# emergency contacts functions

def get_emergency_contacts(user_id: str) -> List[Dict[str, Any]]:
    """get emergency contacts for a user"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if not hasattr(mock_db, 'emergency_contacts'):
            mock_db.emergency_contacts = {}
        return mock_db.emergency_contacts.get(user_id, [])
    
    try:
        db = get_db()
        docs = db.collection("emergency_contacts").where("user_id", "==", user_id).get()
        contacts = [doc_to_dict(d) for d in docs]
        contacts.sort(key=lambda x: x.get("priority", 999))
        return contacts
    except Exception as e:
        print(f"DEBUG: get emergency contacts error: {e}")
        return []


def add_emergency_contact(user_id: str, contact_data: Dict[str, Any]) -> str:
    """add an emergency contact"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if not hasattr(mock_db, 'emergency_contacts'):
            mock_db.emergency_contacts = {}
        if user_id not in mock_db.emergency_contacts:
            mock_db.emergency_contacts[user_id] = []
        contact_id = f"emergency_{len(mock_db.emergency_contacts[user_id]) + 1}"
        contact_data["contact_id"] = contact_id
        contact_data["user_id"] = user_id
        mock_db.emergency_contacts[user_id].append(contact_data)
        return contact_id
    
    try:
        db = get_db()
        contact_data["user_id"] = user_id
        ref = db.collection("emergency_contacts").add(contact_data)
        contact_id = ref[1].id
        contact_data["contact_id"] = contact_id
        db.collection("emergency_contacts").document(contact_id).set(contact_data)
        return contact_id
    except Exception as e:
        print(f"DEBUG: add emergency contact error: {e}")
        return ""


def update_emergency_contact(contact_id: str, updates: Dict[str, Any]) -> bool:
    """update an emergency contact"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'emergency_contacts'):
            for user_id, contacts in mock_db.emergency_contacts.items():
                for c in contacts:
                    if c.get("contact_id") == contact_id:
                        c.update(updates)
                        return True
        return False
    
    try:
        db = get_db()
        db.collection("emergency_contacts").document(contact_id).update(updates)
        return True
    except Exception as e:
        print(f"DEBUG: update emergency contact error: {e}")
        return False


def delete_emergency_contact(contact_id: str) -> bool:
    """delete an emergency contact"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        if hasattr(mock_db, 'emergency_contacts'):
            for user_id, contacts in mock_db.emergency_contacts.items():
                for i, c in enumerate(contacts):
                    if c.get("contact_id") == contact_id:
                        contacts.pop(i)
                        return True
        return False
    
    try:
        db = get_db()
        db.collection("emergency_contacts").document(contact_id).delete()
        return True
    except Exception as e:
        print(f"DEBUG: delete emergency contact error: {e}")
        return False


# third party provider linking

def add_provider_link(user_id: str, link_data: Dict[str, Any]) -> str:
    """store a linked provider account (e.g., google, apple, facebook)"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_provider_link(user_id, link_data)
    
    try:
        db = get_db()
        link_data["user_id"] = user_id
        link_data["linked_at"] = datetime.now().isoformat()
        ref = db.collection("linked_providers").add(link_data)
        link_id = ref[1].id
        link_data["link_id"] = link_id
        db.collection("linked_providers").document(link_id).set(link_data)
        return link_id
    except Exception as e:
        print(f"DEBUG: add provider link error: {e}")
        return ""


def get_provider_links(user_id: str) -> List[Dict[str, Any]]:
    """get all linked provider accounts for a user"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_provider_links(user_id)
    
    try:
        db = get_db()
        docs = db.collection("linked_providers").where("user_id", "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: get provider links error: {e}")
        return []


def delete_provider_link(link_id: str) -> bool:
    """remove a linked provider account"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.delete_provider_link(link_id)
    
    try:
        db = get_db()
        db.collection("linked_providers").document(link_id).delete()
        return True
    except Exception as e:
        print(f"DEBUG: delete provider link error: {e}")
        return False


# social sharing

def create_social_share(user_id: str, share_data: Dict[str, Any]) -> str:
    """store a social share log"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_social_share(user_id, share_data)
    
    try:
        db = get_db()
        share_data["user_id"] = user_id
        share_data["created_at"] = datetime.now().isoformat()
        ref = db.collection("social_shares").add(share_data)
        share_id = ref[1].id
        share_data["share_id"] = share_id
        db.collection("social_shares").document(share_id).set(share_data)
        return share_id
    except Exception as e:
        print(f"DEBUG: create social share error: {e}")
        return ""


def get_social_shares(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """get recent social shares for a user"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_social_shares(user_id)[:limit]
    
    try:
        db = get_db()
        docs = db.collection("social_shares").where("user_id", "==", user_id).limit(limit).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: get social shares error: {e}")
        return []


# appointments and reminders

def create_appointment(appointment: Dict[str, Any]) -> str:
    """store an appointment/reminder for a patient"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_appointment(appointment)
    
    try:
        db = get_db()
        appointment["created_at"] = datetime.now().isoformat()
        ref = db.collection("appointments").add(appointment)
        appt_id = ref[1].id
        appointment["appointment_id"] = appt_id
        db.collection("appointments").document(appt_id).set(appointment)
        return appt_id
    except Exception as e:
        print(f"DEBUG: create appointment error: {e}")
        return ""


def get_appointments_for_user(user_id: str, role: str = "user") -> List[Dict[str, Any]]:
    """get appointments for a patient or provider"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_appointments(user_id)
    
    try:
        db = get_db()
        field = "patient_id" if role != "healthcare_provider" else "provider_id"
        docs = db.collection("appointments").where(field, "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: get appointments error: {e}")
        return []


def update_appointment(appointment_id: str, updates: Dict[str, Any]) -> bool:
    """update appointment details"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        for pid, appointments in mock_db.appointments.items():
            for appt in appointments:
                if appt.get("appointment_id") == appointment_id:
                    appt.update(updates)
                    return True
        return False
    
    try:
        db = get_db()
        db.collection("appointments").document(appointment_id).update(updates)
        return True
    except Exception as e:
        print(f"DEBUG: update appointment error: {e}")
        return False


# support and helpdesk

def create_support_ticket(user_id: str, ticket: Dict[str, Any]) -> str:
    """store a support ticket"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_support_ticket(user_id, ticket)
    
    try:
        db = get_db()
        ticket["user_id"] = user_id
        ticket["created_at"] = datetime.now().isoformat()
        ticket["status"] = ticket.get("status", "open")
        ref = db.collection("support_tickets").add(ticket)
        ticket_id = ref[1].id
        ticket["ticket_id"] = ticket_id
        db.collection("support_tickets").document(ticket_id).set(ticket)
        return ticket_id
    except Exception as e:
        print(f"DEBUG: create ticket error: {e}")
        return ""


def get_support_tickets(user_id: str) -> List[Dict[str, Any]]:
    """get support tickets for a user"""
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_support_tickets(user_id)
    
    try:
        db = get_db()
        docs = db.collection("support_tickets").where("user_id", "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: get support tickets error: {e}")
        return []


# provider and patient management

def get_provider(provider_id: str) -> Optional[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_provider(provider_id)
    try:
        db = get_db()
        doc = db.collection("providers").document(provider_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"DEBUG: get provider error: {e}")
        return None


def upsert_provider_profile(provider_id: str, profile: Dict[str, Any]) -> bool:
    now = datetime.now().isoformat()

    if USE_MOCK:
        from app.core.mock_db import mock_db

        existing = mock_db.providers.get(provider_id, {})
        provider_data = {**existing, **profile}
        provider_data["uid"] = provider_id
        provider_data["role"] = "healthcare_provider"
        provider_data["patients"] = existing.get("patients", [])
        provider_data["created_at"] = existing.get("created_at", now)
        provider_data["updated_at"] = now
        mock_db.providers[provider_id] = provider_data
        return True

    try:
        db = get_db()
        provider_ref = db.collection("providers").document(provider_id)
        provider_doc = provider_ref.get()
        existing = provider_doc.to_dict() if provider_doc.exists else {}
        provider_data = {**existing, **profile}
        provider_data["uid"] = provider_id
        provider_data["role"] = "healthcare_provider"
        provider_data["patients"] = existing.get("patients", [])
        provider_data["created_at"] = existing.get("created_at", now)
        provider_data["updated_at"] = now
        provider_ref.set(provider_data, merge=True)
        return True
    except Exception as e:
        print(f"DEBUG: upsert provider profile error: {e}")
        return False


def add_patient_to_provider(provider_id: str, patient_id: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_patient(provider_id, patient_id)
    
    try:
        db = get_db()
        provider_ref = db.collection("providers").document(provider_id)
        provider_doc = provider_ref.get()
        patients = []
        if provider_doc.exists:
            data = provider_doc.to_dict() or {}
            patients = data.get("patients", [])
        if patient_id not in patients:
            patients.append(patient_id)
        provider_ref.set({"patients": patients}, merge=True)
        return True
    except Exception as e:
        print(f"DEBUG: add patient error: {e}")
        return False


def get_patients_for_provider(provider_id: str) -> List[str]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_patients(provider_id)
    
    try:
        db = get_db()
        doc = db.collection("providers").document(provider_id).get()
        if not doc.exists:
            return []
        data = doc.to_dict() or {}
        return data.get("patients", [])
    except Exception as e:
        print(f"DEBUG: get patients error: {e}")
        return []


def can_provider_access_patient(provider_id: str, patient_id: str) -> bool:
    try:
        patient = get_user(patient_id)
        if not patient:
            return False
        consent = get_consent_settings(patient_id)
        share_ok = consent.get("share_with_healthcare_providers", False)
        patient_ids = get_patients_for_provider(provider_id)
        linked = patient_id in patient_ids
        return share_ok and linked
    except Exception as e:
        print(f"DEBUG: provider access check failed: {e}")
        return False


# provider alerts for patients

def add_patient_alert(provider_id: str, alert: Dict[str, Any]) -> str:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.add_patient_alert(provider_id, alert)
    
    try:
        db = get_db()
        alert["provider_id"] = provider_id
        alert["created_at"] = datetime.now().isoformat()
        alert["enabled"] = alert.get("enabled", True)
        ref = db.collection("provider_alerts").add(alert)
        alert_id = ref[1].id
        alert["alert_id"] = alert_id
        db.collection("provider_alerts").document(alert_id).set(alert)
        return alert_id
    except Exception as e:
        print(f"DEBUG: add provider alert error: {e}")
        return ""


def get_patient_alerts(provider_id: str) -> List[Dict[str, Any]]:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.get_patient_alerts(provider_id)
    
    try:
        db = get_db()
        docs = db.collection("provider_alerts").where("provider_id", "==", provider_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"DEBUG: get provider alerts error: {e}")
        return []


def delete_user_account(user_id: str) -> bool:
    if USE_MOCK:
        from app.core.mock_db import mock_db
        return mock_db.delete_account(user_id)
    try:
        db = get_db()

        db.collection("users").document(user_id).delete()
        db.collection("consent").document(user_id).delete()
        db.collection("mfa_state").document(user_id).delete()

        delete_rules = [
            ("devices", "user_id"),
            ("manual_entries", "user_id"),
            ("biomarkers", "user_id"),
            ("alerts", "user_id"),
            ("linked_providers", "user_id"),
            ("notifications", "user_id"),
            ("emergency_contacts", "user_id"),
            ("social_shares", "user_id"),
            ("support_tickets", "user_id"),
            ("appointments", "patient_id"),
            ("appointments", "provider_id"),
            ("provider_alerts", "patient_id"),
            ("provider_alerts", "provider_id"),
        ]

        for collection_name, field_name in delete_rules:
            docs = db.collection(collection_name).where(field_name, "==", user_id).get()
            for doc in docs:
                doc.reference.delete()

        provider_doc = db.collection("providers").document(user_id).get()
        if provider_doc.exists:
            provider_doc.reference.delete()

        provider_docs = db.collection("providers").get()
        for doc in provider_docs:
            data = doc.to_dict() or {}
            patients = data.get("patients", [])
            if user_id in patients:
                doc.reference.update({
                    "patients": [patient_id for patient_id in patients if patient_id != user_id]
                })

        return True
    except Exception as e:
        print(f"DEBUG: delete account failed: {e}")
        return False
