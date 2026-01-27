from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.biomarker import BiomarkerData, DeviceConnection, ManualDataEntry
from app.core.mock_db import mock_db

def get_firestore():
    try:
        from app.core import firestore
        return firestore
    except:
        return None

router = APIRouter(prefix="/biomarkers", tags=["biomarkers"])

@router.get("/real-time")
async def get_real_time_data(request: Request, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        data = mock_db.get_real_time_data(current_user["uid"])
    else:
        fs = get_firestore()
        data = fs.get_recent_biomarkers(current_user["uid"], limit=5) if fs else []
    
    return {"user_id": current_user["uid"], "data": data}

@router.get("/devices")
async def get_connected_devices(request: Request, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        devices = mock_db.get_user_devices(current_user["uid"])
    else:
        fs = get_firestore()
        devices = fs.get_user_devices(current_user["uid"]) if fs else []
    
    return {"user_id": current_user["uid"], "devices": devices, "count": len(devices)}

@router.post("/manual")
async def add_manual_data(request: Request, data: ManualDataEntry, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        entry_id = mock_db.add_manual_entry(current_user["uid"], data.dict())
        entries = mock_db.get_manual_entries(current_user["uid"])
        new_entry = next((e for e in entries if e["entry_id"] == entry_id), data.dict())
    else:
        fs = get_firestore()
        entry_dict = data.dict()
        if fs:
            entry_id = fs.add_manual_entry(current_user["uid"], entry_dict)
            entries = fs.get_manual_entries(current_user["uid"])
            new_entry = next((e for e in entries if e.get("entry_id") == entry_id), entry_dict)
        else:
            entry_id = "mock_" + str(hash(str(entry_dict)))
            new_entry = entry_dict
            new_entry["entry_id"] = entry_id
    
    return {"message": "Entry created", "user_id": current_user["uid"], "entry_id": entry_id, "data": new_entry}

@router.get("/manual")
async def get_manual_entries(request: Request, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        entries = mock_db.get_manual_entries(current_user["uid"])
    else:
        fs = get_firestore()
        entries = fs.get_manual_entries(current_user["uid"]) if fs else []
    
    return {"user_id": current_user["uid"], "entries": entries, "count": len(entries)}

@router.delete("/manual/{entry_id}")
async def delete_manual_entry(request: Request, entry_id: str, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        return {"message": "Entry deleted (mock)", "entry_id": entry_id}
    else:
        fs = get_firestore()
        success = fs.delete_manual_entry(entry_id) if fs else False
        
        if success:
            return {"message": "Entry deleted", "entry_id": entry_id}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete entry")

@router.get("/historical")
async def get_historical_data(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        return {
            "user_id": current_user["uid"],
            "date_range": {"start": start_date, "end": end_date},
            "summary": {"avg_heart_rate": 70, "total_steps": 12450, "total_calories": 512.3}
        }
    else:
        return {"user_id": current_user["uid"], "message": "Historical data not implemented", "date_range": {"start": start_date, "end": end_date}}