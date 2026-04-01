import json
import os
from datetime import datetime

from app.core.firestore import USE_MOCK, get_db


BACKUP_COLLECTIONS = [
    "users",
    "consent",
    "providers",
    "devices",
    "manual_entries",
    "biomarkers",
    "alerts",
    "provider_alerts",
    "notifications",
    "emergency_contacts",
    "appointments",
    "support_tickets",
    "linked_providers",
    "social_shares",
    "audit_logs",
    "mfa_state",
]


def get_backup_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    backup_dir = os.getenv("PULSELINK_BACKUP_DIR", os.path.join(base_dir, "backups"))
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def create_backup_snapshot() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pulselink_backup_{timestamp}.json"
    backup_path = os.path.join(get_backup_dir(), filename)

    data = {
        "created_at": datetime.now().isoformat(),
        "collections": {},
    }

    if USE_MOCK:
        from app.core.mock_db import mock_db

        data["collections"] = {
            "users": mock_db.users,
            "devices": mock_db.devices,
            "biomarkers": mock_db.biomarkers,
            "providers": mock_db.providers,
            "consent": mock_db.consent,
            "manual_entries": mock_db.manual_entries,
            "linked_providers": mock_db.linked_providers,
            "social_shares": mock_db.social_shares,
            "appointments": mock_db.appointments,
            "support_tickets": mock_db.support_tickets,
            "patient_alerts": mock_db.patient_alerts,
            "notifications": mock_db.notifications,
            "alerts": mock_db.alerts,
            "emergency_contacts": mock_db.emergency_contacts,
            "mfa_state": mock_db.mfa_state,
            "audit_logs": mock_db.audit_logs,
        }
    else:
        db = get_db()
        for collection_name in BACKUP_COLLECTIONS:
            rows = []
            for doc in db.collection(collection_name).stream():
                row = doc.to_dict() or {}
                row["id"] = doc.id
                rows.append(row)
            data["collections"][collection_name] = rows

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {
        "filename": filename,
        "path": backup_path,
        "created_at": data["created_at"],
        "collection_count": len(data["collections"]),
    }


def list_backups() -> list:
    backup_dir = get_backup_dir()
    files = []

    for name in os.listdir(backup_dir):
        if not name.endswith(".json"):
            continue
        full_path = os.path.join(backup_dir, name)
        stat = os.stat(full_path)
        files.append({
            "filename": name,
            "path": full_path,
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })

    files.sort(key=lambda x: x["modified_at"], reverse=True)
    return files
