from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/providers", tags=["healthcare providers"])

@router.get("/patients")
async def get_patients(current_user: dict = Depends(require_role("healthcare_provider"))):
    return {"provider_id": current_user["uid"], "patients": []}

@router.get("/patients/{patient_id}/data")
async def get_patient_data(patient_id: str, current_user: dict = Depends(require_role("healthcare_provider"))):
    return {"provider_id": current_user["uid"], "patient_id": patient_id, "data": "Not implemented"}

@router.post("/alerts")
async def set_patient_alert(patient_id: str, alert_config: dict, current_user: dict = Depends(require_role("healthcare_provider"))):
    return {"status": "Not implemented"}