from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DeviceConnection(BaseModel):
    device_id: str
    device_name: str
    device_type: str  # "smartwatch" "fitness_tracker"  "manual"
    connected_at: datetime
    last_sync: datetime
    is_active: bool = True

class BiomarkerData(BaseModel):
    user_id: str
    device_id: str
    timestamp: datetime
    heart_rate: Optional[int] = None
    steps: Optional[int] = None
    calories: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    sleep_hours: Optional[float] = None
    mood: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = {}

class BiomarkerSummary(BaseModel):
    user_id: str
    period: str  # "daily" "weekly" "monthly"
    start_date: datetime
    end_date: datetime
    avg_heart_rate: Optional[float] = None
    total_steps: Optional[int] = None
    total_calories: Optional[float] = None
    min_values: Dict[str, Optional[float]] = {}
    max_values: Dict[str, Optional[float]] = {}
    data_points: int

class ManualDataEntry(BaseModel):
    biomarker_type: str  # "blood_pressure" "mood" "weight"
    value: Any
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None