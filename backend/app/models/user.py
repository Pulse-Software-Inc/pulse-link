from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: Optional[int] = None
    gender: Optional[str] = None
    language: Optional[str] = "en"

class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    age: Optional[int] = None
    gender: Optional[str] = None
    language: str = "en"
    emergency_contacts: Optional[List[dict]] = []
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    emergency_contacts: Optional[List[dict]] = None

class ConsentSettings(BaseModel):
    share_with_healthcare_providers: bool = False
    share_anonymized_data: bool = False
    data_retention_days: int = 7   #change to 7

class DashboardCustomization(BaseModel):
    visible_metrics: List[str] = ["heart_rate", "steps", "calories"]
    theme: str = "default"
    layout: dict = {}