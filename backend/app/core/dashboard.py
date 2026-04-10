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


DEFAULT_DASHBOARD_CUSTOMIZATION = {
    "visible_metrics": ["heart_rate", "steps", "calories", "sleep_hours"],
    "theme": "default",
    "layout": {},
}


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
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
        "id": device.get("id") or device.get("device_id"),
        "device_name": device.get("device_name", ""),
        "device_type": device.get("device_type", ""),
        "brand": device.get("brand", ""),
        "connected_at": device.get("connected_at") or device.get("created_at"),
        "is_active": bool(device.get("is_active", True)),
        "last_sync": device.get("last_sync"),
    }


def get_dashboard_customization(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    customization = DEFAULT_DASHBOARD_CUSTOMIZATION.copy()
    customization.update((user or {}).get("dashboard_customization") or {})
    customization["visible_metrics"] = list(customization.get("visible_metrics") or DEFAULT_DASHBOARD_CUSTOMIZATION["visible_metrics"])
    customization["layout"] = customization.get("layout") or {}
    return customization


def _sorted_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: parse_timestamp(record.get("timestamp")) or datetime.min,
    )


def _latest_record(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    ordered = _sorted_records(records)
    return ordered[-1] if ordered else None


def _anchor_date(records: List[Dict[str, Any]], fallback: Optional[datetime] = None) -> datetime.date:
    latest = _latest_record(records)
    latest_dt = parse_timestamp((latest or {}).get("timestamp"))
    if latest_dt:
        return latest_dt.date()
    return (fallback or datetime.now()).date()


def _date_range(anchor_date: datetime.date) -> List[datetime.date]:
    return [anchor_date - timedelta(days=offset) for offset in range(6, -1, -1)]


def _daily_record_buckets(records: List[Dict[str, Any]], anchor_date: Optional[datetime.date] = None) -> Dict[str, Dict[str, Any]]:
    target_date = anchor_date or _anchor_date(records)
    buckets = {
        day.isoformat(): {
            "records": [],
            "steps": [],
            "calories": [],
            "heart_rates": [],
        }
        for day in _date_range(target_date)
    }

    for record in _sorted_records(records):
        record_dt = parse_timestamp(record.get("timestamp"))
        if not record_dt:
            continue
        key = record_dt.date().isoformat()
        if key not in buckets:
            continue
        buckets[key]["records"].append(record)
        steps = record.get("steps")
        if isinstance(steps, (int, float)):
            buckets[key]["steps"].append(float(steps))
        calories = record.get("calories")
        if isinstance(calories, (int, float)):
            buckets[key]["calories"].append(float(calories))
        heart_rate = record.get("heart_rate")
        if isinstance(heart_rate, (int, float)):
            buckets[key]["heart_rates"].append(float(heart_rate))

    return buckets


def serialize_biomarker(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id") or record.get("biomarker_id"),
        "user_id": record.get("user_id"),
        "device_id": record.get("device_id"),
        "timestamp": record.get("timestamp"),
        "heart_rate": record.get("heart_rate"),
        "steps": record.get("steps"),
        "calories": record.get("calories"),
        "blood_pressure_systolic": record.get("blood_pressure_systolic"),
        "blood_pressure_diastolic": record.get("blood_pressure_diastolic"),
        "sleep_hours": record.get("sleep_hours"),
        "mood": record.get("mood"),
        "additional_data": record.get("additional_data", {}) or {},
    }


def build_daily_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered = _sorted_records(records)
    anchor = _anchor_date(ordered)
    day_records = [
        record for record in ordered
        if (parse_timestamp(record.get("timestamp")) or datetime.min).date() == anchor
    ]
    heart_rates = [float(record["heart_rate"]) for record in day_records if isinstance(record.get("heart_rate"), (int, float))]
    steps_values = [float(record["steps"]) for record in day_records if isinstance(record.get("steps"), (int, float))]
    calories_values = [float(record["calories"]) for record in day_records if isinstance(record.get("calories"), (int, float))]
    return {
        "period": "daily",
        "start_date": f"{anchor.isoformat()}T00:00:00Z",
        "end_date": f"{anchor.isoformat()}T23:59:59Z",
        "avg_heart_rate": round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else 0,
        "total_steps": int(max(steps_values)) if steps_values else 0,
        "total_calories": round(max(calories_values), 1) if calories_values else 0,
        "min_values": {
            "heart_rate": int(min(heart_rates)) if heart_rates else None,
            "steps": int(min(steps_values)) if steps_values else None,
        },
        "max_values": {
            "heart_rate": int(max(heart_rates)) if heart_rates else None,
            "steps": int(max(steps_values)) if steps_values else None,
        },
        "data_points": len(day_records),
    }


def build_weekly_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    anchor = _anchor_date(records)
    buckets = _daily_record_buckets(records, anchor)
    daily_steps = []
    for day in _date_range(anchor):
        key = day.isoformat()
        values = buckets[key]["steps"]
        daily_steps.append({
            "date": key,
            "steps": int(max(values)) if values else 0,
        })

    total_steps = sum(day["steps"] for day in daily_steps)
    return {
        "week_start": daily_steps[0]["date"] if daily_steps else anchor.isoformat(),
        "week_end": daily_steps[-1]["date"] if daily_steps else anchor.isoformat(),
        "daily_steps": daily_steps,
        "average_steps": round(total_steps / len(daily_steps)) if daily_steps else 0,
        "total_distance_km": round(total_steps * 0.00075, 1),
        "active_days": len([day for day in daily_steps if day["steps"] > 0]),
    }


def _time_label(timestamp: Optional[str]) -> str:
    dt = parse_timestamp(timestamp)
    if not dt:
        return ""
    return dt.strftime("%I%p").lstrip("0").lower()


def build_heart_rate_daily(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered = _sorted_records(records)
    anchor = _anchor_date(ordered)
    heart_records = [
        record for record in ordered
        if (parse_timestamp(record.get("timestamp")) or datetime.min).date() == anchor
        and isinstance(record.get("heart_rate"), (int, float))
    ]
    points = [
        {
            "label": _time_label(record.get("timestamp")),
            "bpm": int(record["heart_rate"]),
        }
        for record in heart_records[-7:]
    ]
    bpm_values = [point["bpm"] for point in points]
    resting = min(bpm_values) if bpm_values else 0
    average = round(sum(bpm_values) / len(bpm_values)) if bpm_values else 0
    peak = max(bpm_values) if bpm_values else 0
    return {
        "resting_bpm": resting,
        "average_bpm": average,
        "peak_bpm": peak,
        "y_min": max(40, resting - 20) if bpm_values else 40,
        "y_max": max(120, peak + 20) if bpm_values else 120,
        "points": points,
    }


def build_recent_biomarkers(records: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    ordered = _sorted_records(records)
    return [serialize_biomarker(record) for record in ordered[-limit:]]


def build_weekly_patient_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    weekly = build_weekly_summary(records)
    heart_rates = [
        float(record["heart_rate"])
        for record in records
        if isinstance(record.get("heart_rate"), (int, float))
    ]
    calories = [
        float(record["calories"])
        for record in records
        if isinstance(record.get("calories"), (int, float))
    ]
    return {
        "period": "weekly",
        "avg_heart_rate": round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else 0,
        "total_steps": sum(day["steps"] for day in weekly["daily_steps"]),
        "total_calories": round(sum(calories), 1) if calories else 0,
        "data_points": len(records),
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
