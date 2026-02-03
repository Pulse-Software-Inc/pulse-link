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
