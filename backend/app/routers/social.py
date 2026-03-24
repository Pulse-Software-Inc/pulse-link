#!/usr/bin/env python3
"""social sharing endpoints - log shared stats/achievements"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/social", tags=["social sharing"])


@router.get("/shares")
async def get_shares(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """get recent social share logs for the user"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        shares = firestore.get_social_shares(uid, limit=limit)
        return {
            "user_id": uid,
            "shares": shares,
            "count": len(shares)
        }
    except Exception as e:
        print(f"DEBUG: get shares error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch shares")


@router.post("/share")
async def create_share(
    payload: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    log that the user shared a stat/achievement to a platform.
    this does not post to the network; it stores the intent for auditing.
    """
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        platform = payload.get("platform", "").lower().strip()
        metric = payload.get("metric", "").strip()
        
        if not platform:
            raise HTTPException(status_code=400, detail="platform is required")
        if platform not in ["google", "facebook", "apple", "twitter", "instagram", "linkedin", "whatsapp", "other"]:
            platform = "other"
        
        share_data = {
            "platform": platform,
            "metric": metric or "achievement",
            "message": payload.get("message", ""),
            "visibility": payload.get("visibility", "friends"),
            "created_at": datetime.now().isoformat()
        }
        
        share_id = firestore.create_social_share(uid, share_data)
        
        if not share_id:
            raise HTTPException(status_code=500, detail="failed to log share")
        
        return {
            "user_id": uid,
            "share_id": share_id,
            "message": "share logged",
            "share": share_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: create share error: {e}")
        raise HTTPException(status_code=500, detail="failed to log share")
