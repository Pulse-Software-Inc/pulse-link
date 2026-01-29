from firebase_admin import firestore as fs
from typing import Dict, Any, List, Optional
from datetime import datetime

db = None

def get_db():
    global db
    if db is None:
        try:
            db = fs.client()
        except:
            db = None
    return db

def get_user(uid: str) -> Optional[Dict[str, Any]]:
    try:
        client = get_db()
        if not client:
            return None
        doc = client.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error getting user {uid}: {e}")
        return None

def update_user(uid: str, data: Dict[str, Any]) -> bool:
    try:
        client = get_db()
        if not client:
            return False
        data["updated_at"] = datetime.now().isoformat()
        client.collection("users").document(uid).update(data)
        return True
    except Exception as e:
        print(f"Error updating user {uid}: {e}")
        return False

def create_user(uid: str, user_data: Dict[str, Any]) -> bool:
    try:
        client = get_db()
        if not client:
            return False
        user_data["created_at"] = datetime.now().isoformat()
        user_data["updated_at"] = datetime.now().isoformat()
        client.collection("users").document(uid).set(user_data)
        return True
    except Exception as e:
        print(f"Error creating user {uid}: {e}")
        return False

def get_user_devices(user_id: str) -> List[Dict[str, Any]]:
    try:
        client = get_db()
        if not client:
            return []
        docs = client.collection("devices").where("user_id", "==", user_id).get()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting devices for user {user_id}: {e}")
        return []

def add_device(user_id: str, device_data: Dict[str, Any]) -> str:
    try:
        client = get_db()
        if not client:
            return ""
        device_data["user_id"] = user_id
        device_data["created_at"] = datetime.now().isoformat()
        device_data["updated_at"] = datetime.now().isoformat()
        ref = client.collection("devices").add(device_data)
        return ref[1].id
    except Exception as e:
        print(f"Error adding device for user {user_id}: {e}")
        return ""

def get_manual_entries(user_id: str) -> List[Dict[str, Any]]:
    try:
        client = get_db()
        if not client:
            return []
        docs = client.collection("manual_entries").where("user_id", "==", user_id).get()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting manual entries for user {user_id}: {e}")
        return []

def add_manual_entry(user_id: str, entry_data: Dict[str, Any]) -> str:
    try:
        client = get_db()
        if not client:
            return ""
        entry_data["user_id"] = user_id
        entry_data["timestamp"] = datetime.now().isoformat()
        ref = client.collection("manual_entries").add(entry_data)
        return ref[1].id
    except Exception as e:
        print(f"Error adding manual entry for user {user_id}: {e}")
        return ""

def get_recent_biomarkers(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        client = get_db()
        if not client:
            return []
        docs = client.collection("biomarkers").where("user_id", "==", user_id).limit(limit).get()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting biomarkers for user {user_id}: {e}")
        return []

def get_consent_settings(user_id: str) -> Dict[str, Any]:
    try:
        client = get_db()
        if not client:
            return {}
        doc = client.collection("consent").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return {
            "share_with_healthcare_providers": False,
            "share_anonymized_data": False,
            "data_retention_days": 7
        }
    except Exception as e:
        print(f"Error getting consent for user {user_id}: {e}")
        return {}

def update_consent_settings(user_id: str, settings: Dict[str, Any]) -> bool:
    try:
        client = get_db()
        if not client:
            return False
        client.collection("consent").document(user_id).set(settings)
        return True
    except Exception as e:
        print(f"Error updating consent for user {user_id}: {e}")
        return False