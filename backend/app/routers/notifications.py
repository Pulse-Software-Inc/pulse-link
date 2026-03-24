#!/usr/bin/env python3
"""notifications router - in-app notifications for users"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

# notifications are stored in firestore, not sent as push
# this is for in-app notification center

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    get user's notifications.
    use unread_only=true to see only unread messages.
    """
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get notifications from firestore
        notifications = firestore.get_user_notifications(uid, limit=limit)
        
        # filter unread if requested
        if unread_only:
            notifications = [n for n in notifications if not n.get("read", False)]
        
        # count unread
        unread_count = len([n for n in notifications if not n.get("read", False)])
        
        print(f"DEBUG: fetched {len(notifications)} notifications for user {uid}")
        
        return {
            "user_id": uid,
            "notifications": notifications,
            "count": len(notifications),
            "unread_count": unread_count
        }
        
    except Exception as e:
        print(f"DEBUG: get notifications error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch notifications")


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """mark a notification as read"""
    from app.core import firestore
    
    try:
        success = firestore.mark_notification_read(notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="notification not found")
        
        return {
            "user_id": current_user["uid"],
            "notification_id": notification_id,
            "message": "marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: mark read error: {e}")
        raise HTTPException(status_code=500, detail="failed to mark notification")


@router.post("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """mark all notifications as read"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        count = firestore.mark_all_notifications_read(uid)
        
        return {
            "user_id": uid,
            "marked_as_read": count,
            "message": f"{count} notifications marked as read"
        }
        
    except Exception as e:
        print(f"DEBUG: mark all read error: {e}")
        raise HTTPException(status_code=500, detail="failed to mark notifications")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """delete a notification"""
    from app.core import firestore
    
    try:
        success = firestore.delete_notification(notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="notification not found")
        
        return {
            "user_id": current_user["uid"],
            "notification_id": notification_id,
            "message": "notification deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: delete notification error: {e}")
        raise HTTPException(status_code=500, detail="failed to delete notification")


@router.get("/summary")
async def get_notification_summary(current_user: dict = Depends(get_current_user)):
    """get summary of notifications (for dashboard badge)"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get recent notifications
        notifications = firestore.get_user_notifications(uid, limit=100)
        
        # calculate stats
        unread = [n for n in notifications if not n.get("read", False)]
        
        # group by type
        types = {}
        for n in notifications:
            t = n.get("type", "general")
            types[t] = types.get(t, 0) + 1
        
        # recent alerts (last 24 hours)
        now = datetime.now()
        recent = []
        for n in notifications:
            try:
                created = n.get("created_at", "")
                if created:
                    n_time = datetime.fromisoformat(created)
                    if now - n_time < timedelta(hours=24):
                        recent.append(n)
            except:
                pass
        
        return {
            "user_id": uid,
            "total_notifications": len(notifications),
            "unread_count": len(unread),
            "recent_24h": len(recent),
            "by_type": types,
            "has_unread": len(unread) > 0
        }
        
    except Exception as e:
        print(f"DEBUG: summary error: {e}")
        raise HTTPException(status_code=500, detail="failed to get summary")


# internal endpoint to create notification (called by other services)
def create_notification_internal(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "general",
    data: dict = None
) -> str:
    """internal function to create a notification - called by alert system"""
    from app.core import firestore
    
    try:
        notification = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
            "data": data or {},
            "created_at": datetime.now().isoformat()
        }
        
        notif_id = firestore.create_notification(notification)
        print(f"DEBUG: created notification {notif_id} for user {user_id}")
        return notif_id
        
    except Exception as e:
        print(f"DEBUG: create notification error: {e}")
        return ""
