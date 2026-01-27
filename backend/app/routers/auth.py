from fastapi import APIRouter, Depends
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.user import UserProfile

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/me", response_model=Dict)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"],
        "message": "Authentication successful"
    }

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    return {"status": "valid", "user": current_user}