from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.user import UserUpdate, ConsentSettings, DashboardCustomization
from app.core.mock_db import mock_db

def get_firestore_helpers():
    try:
        from app.core import firestore as fs_helpers
        return fs_helpers
    except:
        return None

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_user_profile(request: Request, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        user = mock_db.get_user(current_user["uid"])
    else:
        fs_helpers = get_firestore_helpers()
        user = fs_helpers.get_user(current_user["uid"]) if fs_helpers else None
    
    if not user:
        if not use_mock:
            user_data = {
                "uid": current_user["uid"],
                "email": current_user["email"],
                "role": current_user.get("role", "user"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            fs_helpers = get_firestore_helpers()
            if fs_helpers and fs_helpers.create_user(current_user["uid"], user_data):
                user = user_data
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

@router.put("/me")
async def update_user_profile(request: Request, profile_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    updates = profile_update.dict(exclude_unset=True)
    
    if use_mock:
        updated = mock_db.update_user(current_user["uid"], updates)
    else:
        fs_helpers = get_firestore_helpers()
        updated = fs_helpers.update_user(current_user["uid"], updates) if fs_helpers else False
    
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if use_mock:
        updated_user = mock_db.get_user(current_user["uid"])
    else:
        fs_helpers = get_firestore_helpers()
        updated_user = fs_helpers.get_user(current_user["uid"]) if fs_helpers else None
    
    return {"message": "Profile updated", "user": updated_user}

@router.get("/me/consent")
async def get_consent_settings(request: Request, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        return {
            "user_id": current_user["uid"],
            "consent": {"share_with_healthcare_providers": True, "share_anonymized_data": False, "data_retention_days": 365}
        }
    else:
        fs_helpers = get_firestore_helpers()
        consent = fs_helpers.get_consent_settings(current_user["uid"]) if fs_helpers else {}
        return {"user_id": current_user["uid"], "consent": consent}

@router.put("/me/consent")
async def update_consent_settings(request: Request, consent: ConsentSettings, current_user: dict = Depends(get_current_user)):
    use_mock = request.app.state.use_mock
    
    if use_mock:
        return {"user_id": current_user["uid"], "message": "Consent updated (mock)", "consent": consent}
    else:
        fs_helpers = get_firestore_helpers()
        success = fs_helpers.update_consent_settings(current_user["uid"], consent.dict()) if fs_helpers else False
        
        if success:
            return {"user_id": current_user["uid"], "message": "Consent updated", "consent": consent}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update consent")