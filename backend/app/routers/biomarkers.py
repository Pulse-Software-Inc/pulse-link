from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import Optional
import sys
import os

# fix path so we can import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.biomarker import ManualDataEntry

router = APIRouter(prefix="/biomarkers", tags=["biomarkers"])


@router.get("/real-time")
async def get_real_time_data(
    request: Request, current_user: dict = Depends(get_current_user)
):
    # import here to avoid circular imports
    from app.core import firestore
    
    try:
        data = firestore.get_recent_biomarkers(current_user["uid"], limit=5)
        return {"user_id": current_user["uid"], "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def get_connected_devices(
    request: Request, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        devices = firestore.get_user_devices(current_user["uid"])
        return {"user_id": current_user["uid"], "devices": devices, "count": len(devices)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {e}")


@router.post("/manual")
async def add_manual_data(
    request: Request, data: ManualDataEntry, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        entry_dict = data.dict()
        entry_id = firestore.add_manual_entry(current_user["uid"], entry_dict)
        
        # fetch the entry we just created
        entries = firestore.get_manual_entries(current_user["uid"])
        new_entry = None
        for e in entries:
            if e.get("entry_id") == entry_id:
                new_entry = e
                break
        
        if not new_entry:
            new_entry = entry_dict
        
        return {
            "message": "Entry created",
            "user_id": current_user["uid"],
            "entry_id": entry_id,
            "data": new_entry,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add entry: {e}")


@router.get("/manual")
async def get_manual_entries(
    request: Request, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        entries = firestore.get_manual_entries(current_user["uid"])
        return {"user_id": current_user["uid"], "entries": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/manual/{entry_id}")
async def delete_manual_entry(
    request: Request, entry_id: str, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        success = firestore.delete_manual_entry(entry_id)
        if success:
            return {"message": "Entry deleted", "entry_id": entry_id}
        else:
            raise HTTPException(status_code=500, detail="Delete failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    # TODO: implement this properly
    return {
        "user_id": current_user["uid"],
        "message": "Historical data not implemented yet",
        "date_range": {"start": start_date, "end": end_date},
    }
