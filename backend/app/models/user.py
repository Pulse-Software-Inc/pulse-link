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
    emergency_contacts: Optional[List[dict]] = None


class ConsentSettings(BaseModel):
    share_with_healthcare_providers: bool = False
    share_anonymized_data: bool = False
    data_retention_days: int = 7  # changed to 7 as per requirements


class DashboardCustomization(BaseModel):
    visible_metrics: List[str] = ["heart_rate", "steps", "calories"]
    theme: str = "default"
    layout: dict = {}
