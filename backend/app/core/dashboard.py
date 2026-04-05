from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


DEFAULT_DAILY_GOALS = {
    "steps": 10000,
    "calories": 2500,
    "heart_rate": 80,
}


DEFAULT_EMERGENCY_SETTINGS = {
    "auto_alert_enabled": True,
    "heart_rate_threshold": 180,
    "fall_detection_enabled": True,
    "location_sharing_enabled": True,
    "alert_delay_seconds": 30,
}


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def get_daily_goals(user: Optional[Dict[str, Any]]) -> Dict[str, int]:
    goals = DEFAULT_DAILY_GOALS.copy()
    stored = (user or {}).get("daily_goals") or {}
    for key in goals:
        value = stored.get(key)
        if isinstance(value, (int, float)) and value > 0:
            goals[key] = int(value)
    return goals


def get_emergency_settings(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    settings = DEFAULT_EMERGENCY_SETTINGS.copy()
    settings.update((user or {}).get("emergency_settings") or {})
    return settings


def serialize_device(device: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "device_id": device.get("device_id") or device.get("id"),
        "device_name": device.get("device_name", ""),
        "device_type": device.get("device_type", ""),
        "brand": device.get("brand", ""),
        "is_active": bool(device.get("is_active", True)),
        "last_sync": device.get("last_sync"),
    }


def build_last_7_days_metrics(records: List[Dict[str, Any]], end_date: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
    anchor = end_date or datetime.now()
    days = [(anchor.date() - timedelta(days=offset)) for offset in range(6, -1, -1)]
    buckets: Dict[str, Dict[str, Any]] = {
        day.isoformat(): {
            "steps": None,
            "calories": None,
            "heart_rate_values": [],
        }
        for day in days
    }

    for record in records:
        record_dt = parse_timestamp(record.get("timestamp"))
        if not record_dt:
            continue
        date_key = record_dt.date().isoformat()
        if date_key not in buckets:
            continue

        steps = record.get("steps")
        if isinstance(steps, (int, float)):
            buckets[date_key]["steps"] = int((buckets[date_key]["steps"] or 0) + steps)

        calories = record.get("calories")
        if isinstance(calories, (int, float)):
            buckets[date_key]["calories"] = int((buckets[date_key]["calories"] or 0) + calories)

        heart_rate = record.get("heart_rate")
        if isinstance(heart_rate, (int, float)):
            buckets[date_key]["heart_rate_values"].append(int(heart_rate))

    metrics: Dict[str, List[Dict[str, Any]]] = {
        "steps": [],
        "calories": [],
        "heart_rate": [],
    }

    for day in days:
        date_key = day.isoformat()
        bucket = buckets[date_key]

        metrics["steps"].append({
            "date": date_key,
            "value": bucket["steps"] if bucket["steps"] is not None else "N/A",
        })
        metrics["calories"].append({
            "date": date_key,
            "value": bucket["calories"] if bucket["calories"] is not None else "N/A",
        })

        heart_rates = bucket["heart_rate_values"]
        metrics["heart_rate"].append({
            "date": date_key,
            "value": round(sum(heart_rates) / len(heart_rates)) if heart_rates else "N/A",
        })

    return metrics
