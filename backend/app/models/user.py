from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: str
    password: str
    first_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("first_name", "firstName", "firstname"))
    last_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("last_name", "lastName", "lastname"))
    role: Optional[str] = "user"
    age: Optional[int] = None
    language: Optional[str] = "en"


class UserProfile(BaseModel):
    uid: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    age: Optional[int] = None
    language: str = "en"
    ai_instructions: str = ""
    daily_goals: Optional[dict] = None
    emergency_contacts: Optional[List[dict]] = []  # might change this later
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    first_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("first_name", "firstName", "firstname"))
    last_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("last_name", "lastName", "lastname"))
    email: Optional[str] = None
    role: Optional[str] = None
    age: Optional[int] = None
    language: Optional[str] = None
    ai_instructions: Optional[str] = Field(default=None, validation_alias=AliasChoices("ai_instructions", "aiInstructions"))
    daily_goals: Optional[dict] = Field(default=None, validation_alias=AliasChoices("daily_goals", "dailyGoals"))
    emergency_contacts: Optional[List[dict]] = None


class ConsentSettings(BaseModel):
    share_with_healthcare_providers: bool = False
    share_anonymized_data: bool = False
    data_retention_days: int = 7  # changed to 7 as per requirements


class DashboardCustomization(BaseModel):
    visible_metrics: List[str] = ["heart_rate", "steps", "calories"]
    theme: str = "default"
    layout: dict = {}


class DailyGoals(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    steps: int = Field(default=10000, validation_alias=AliasChoices("steps"))
    calories: int = Field(default=2500, validation_alias=AliasChoices("calories"))
    heart_rate: int = Field(default=80, validation_alias=AliasChoices("heart_rate", "heartRate"))


class DeviceSettingsItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    device_id: Optional[str] = Field(default=None, validation_alias=AliasChoices("device_id", "id"))
    device_name: str = Field(validation_alias=AliasChoices("device_name", "deviceName"))
    device_type: str = Field(validation_alias=AliasChoices("device_type", "deviceType"))
    brand: str = ""
    is_active: bool = Field(default=True, validation_alias=AliasChoices("is_active", "isActive"))
    last_sync: Optional[str] = Field(default=None, validation_alias=AliasChoices("last_sync", "lastSync"))


class ProviderClientInviteItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: str
    message: str = ""
    status: str = "pending"


class UserSettingsUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    first_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("first_name", "firstName", "firstname", "fname"))
    last_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("last_name", "lastName", "lastname", "lname"))
    email: Optional[str] = None
    language: Optional[str] = None
    ai_instructions: Optional[str] = Field(default=None, validation_alias=AliasChoices("ai_instructions", "aiInstructions"))
    daily_goals: Optional[DailyGoals] = Field(default=None, validation_alias=AliasChoices("daily_goals", "dailyGoals"))
    notification_preferences: Optional[dict] = Field(default=None, validation_alias=AliasChoices("notification_preferences", "notificationPreferences"))
    emergency_settings: Optional[dict] = Field(default=None, validation_alias=AliasChoices("emergency_settings", "emergencySettings"))
    devices: Optional[List[DeviceSettingsItem]] = None
    invite_clients: Optional[List[ProviderClientInviteItem]] = Field(default=None, validation_alias=AliasChoices("invite_clients", "inviteClients"))
