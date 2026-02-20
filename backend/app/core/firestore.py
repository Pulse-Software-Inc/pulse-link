from firebase_admin import firestore as fs
from typing import Dict, Any, List, Optional
from datetime import datetime

_db = None

def get_db():
    global _db
    if _db is None:
        _db = fs.client()
    return _db


def get_user(uid: str) -> Optional[Dict[str, Any]]:
    client = get_db()
    try:
        doc = client.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        # TODO: handle this better
        print(f"Failed to get user: {e}")
        return None


def update_user(uid: str, data: Dict[str, Any]) -> bool:
    try:
        db = get_db()
        data["updated_at"] = datetime.now().isoformat()
        db.collection("users").document(uid).update(data)
        return True
    except Exception:
        # forgot to add error message here
        return False


def create_user(uid: str, user_data: Dict[str, Any]) -> bool:
    db = get_db()
    try:
        now = datetime.now().isoformat()
        if "created_at" not in user_data:
            user_data["created_at"] = now
        user_data["updated_at"] = now
        db.collection("users").document(uid).set(user_data)
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
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


def get_manual_entries(user_id: str) -> List[Dict[str, Any]]:
    try:
        db = get_db()
        docs = db.collection("manual_entries").where("user_id", "==", user_id).get()
        return [doc_to_dict(doc) for doc in docs]
    except:
        return []


def add_manual_entry(user_id: str, entry_data: Dict[str, Any]) -> str:
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
    try:
        client = get_db()
        client.collection("manual_entries").document(entry_id).delete()
        return True
    except Exception as e:
        print(f"Delete failed for {entry_id}: {e}")
        return False


def get_recent_biomarkers(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        db = get_db()
        docs = db.collection("biomarkers").where("user_id", "==", user_id).limit(limit).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"Error getting biomarkers: {e}")
        return []


def get_all_biomarkers(user_id: str) -> List[Dict[str, Any]]:
    # get all biomarkers for a user (for export)
    try:
        db = get_db()
        docs = db.collection("biomarkers").where("user_id", "==", user_id).get()
        return [doc_to_dict(d) for d in docs]
    except Exception as e:
        print(f"Error getting all biomarkers: {e}")
        return []


def get_consent_settings(user_id: str) -> Dict[str, Any]:
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
    try:
        db = get_db()
        db.collection("consent").document(user_id).set(settings)
        return True
    except Exception as e:
        print(f"Consent update failed: {e}")
        return False


def doc_to_dict(doc):
    """convert doc to dict with id"""
    d = doc.to_dict()
    d["id"] = doc.id
    return d
