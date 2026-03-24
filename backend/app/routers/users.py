from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, List
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.user import UserUpdate, ConsentSettings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_user_profile(request: Request, current_user: dict = Depends(get_current_user)):
    from app.core import firestore
    
    user = firestore.get_user(current_user["uid"])
    
    # if user doesn't exist, create them
    if not user:
        print(f"Creating new user: {current_user['uid']}")
        user_data = {
            "uid": current_user["uid"],
            "email": current_user["email"],
            "role": current_user.get("role", "user"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        if firestore.create_user(current_user["uid"], user_data):
            user = user_data
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/me")
async def update_user_profile(request: Request, profile_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    from app.core import firestore
    
    updates = profile_update.dict(exclude_unset=True)
    
    # update the user
    updated = firestore.update_user(current_user["uid"], updates)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Failed to update user")
    
    # fetch updated user
    updated_user = firestore.get_user(current_user["uid"])
    return {"message": "Profile updated", "user": updated_user}


@router.get("/me/consent")
async def get_consent_settings(request: Request, current_user: dict = Depends(get_current_user)):
    from app.core import firestore
    
    consent = firestore.get_consent_settings(current_user["uid"])
    return {"user_id": current_user["uid"], "consent": consent}


@router.put("/me/consent")
async def update_consent_settings(request: Request, consent: ConsentSettings, current_user: dict = Depends(get_current_user)):
    from app.core import firestore
    
    success = firestore.update_consent_settings(current_user["uid"], consent.dict())
    
    if success:
        return {
            "user_id": current_user["uid"], 
            "message": "Consent updated", 
            "consent": consent
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update consent")


# --- third-party provider linking (google/apple/facebook) ---

@router.get("/me/providers")
async def get_linked_providers(current_user: dict = Depends(get_current_user)):
    """get third-party accounts linked to the user"""
    from app.core import firestore
    try:
        uid = current_user["uid"]
        links = firestore.get_provider_links(uid)
        return {"user_id": uid, "linked_providers": links, "count": len(links)}
    except Exception as e:
        print(f"DEBUG: get providers error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch provider links")


@router.post("/me/providers")
async def link_provider_account(payload: dict, current_user: dict = Depends(get_current_user)):
    """store metadata for a linked provider account (oauth handled on client)"""
    from app.core import firestore
    try:
        uid = current_user["uid"]
        provider = (payload.get("provider") or "").lower().strip()
        if provider not in ["google", "apple", "facebook"]:
            raise HTTPException(status_code=400, detail="provider must be google, apple, or facebook")
        
        link_data = {
            "provider": provider,
            "external_id": payload.get("external_id", ""),
            "email": payload.get("email", current_user.get("email")),
            "linked_at": datetime.now().isoformat(),
            "scopes": payload.get("scopes", []),
        }
        
        link_id = firestore.add_provider_link(uid, link_data)
        if not link_id:
            raise HTTPException(status_code=500, detail="failed to link provider")
        
        return {"user_id": uid, "link_id": link_id, "message": "provider linked", "provider": provider}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: link provider error: {e}")
        raise HTTPException(status_code=500, detail="failed to link provider")


@router.delete("/me/providers/{link_id}")
async def remove_provider_link(link_id: str, current_user: dict = Depends(get_current_user)):
    """unlink a provider account"""
    from app.core import firestore
    try:
        success = firestore.delete_provider_link(link_id)
        if not success:
            raise HTTPException(status_code=404, detail="link not found")
        return {"user_id": current_user["uid"], "link_id": link_id, "message": "provider unlinked"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: delete provider link error: {e}")
        raise HTTPException(status_code=500, detail="failed to unlink provider")


# --- custom alerts endpoints ---

@router.get("/me/alerts")
async def get_user_alerts(request: Request, current_user: dict = Depends(get_current_user)):
    """get all custom alert thresholds for the current user"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        alerts = firestore.get_user_alerts(uid)
        
        print(f"DEBUG: fetched {len(alerts)} alerts for user {uid}")
        
        return {
            "user_id": uid,
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        print(f"DEBUG: error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=f"failed to fetch alerts: {e}")


@router.post("/me/alerts")
async def create_alert(
    request: Request, 
    alert_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """create a new custom alert threshold"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # validate required fields
        required = ["biomarker_type", "condition", "threshold"]
        for field in required:
            if field not in alert_data:
                raise HTTPException(status_code=400, detail=f"missing required field: {field}")
        
        # validate condition
        valid_conditions = ["greater_than", "less_than", "equals"]
        if alert_data["condition"] not in valid_conditions:
            raise HTTPException(status_code=400, detail=f"invalid condition. must be one of: {valid_conditions}")
        
        # validate biomarker type
        valid_types = ["heart_rate", "steps", "calories", "sleep_hours", "blood_pressure_systolic", "blood_pressure_diastolic"]
        if alert_data["biomarker_type"] not in valid_types:
            raise HTTPException(status_code=400, detail=f"invalid biomarker_type. must be one of: {valid_types}")
        
        # set defaults
        alert_data.setdefault("message", f"{alert_data['biomarker_type']} is {alert_data['condition']} {alert_data['threshold']}")
        alert_data.setdefault("enabled", True)
        
        alert_id = firestore.create_alert(uid, alert_data)
        
        if not alert_id:
            raise HTTPException(status_code=500, detail="failed to create alert")
        
        print(f"DEBUG: created alert {alert_id} for user {uid}")
        
        return {
            "user_id": uid,
            "alert_id": alert_id,
            "message": "alert created successfully",
            "alert": alert_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: error creating alert: {e}")
        raise HTTPException(status_code=500, detail=f"failed to create alert: {e}")


@router.delete("/me/alerts/{alert_id}")
async def delete_alert(
    request: Request,
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """delete an alert threshold"""
    from app.core import firestore
    
    try:
        success = firestore.delete_alert(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="alert not found")
        
        print(f"DEBUG: deleted alert {alert_id}")
        
        return {
            "user_id": current_user["uid"],
            "alert_id": alert_id,
            "message": "alert deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: error deleting alert: {e}")
        raise HTTPException(status_code=500, detail=f"failed to delete alert: {e}")
