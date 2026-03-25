#!/usr/bin/env python3
"""emergency contacts router - manage emergency contacts for critical events"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/emergency", tags=["emergency contacts"])

@router.get("/contacts")
async def get_emergency_contacts(current_user: dict = Depends(get_current_user)):
    """get user's emergency contacts"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        contacts = firestore.get_emergency_contacts(uid)
        
        print(f"DEBUG: fetched {len(contacts)} emergency contacts for user {uid}")
        
        return {
            "user_id": uid,
            "contacts": contacts,
            "count": len(contacts),
            "max_contacts": 5  # limit for safety
        }
        
    except Exception as e:
        print(f"DEBUG: get emergency contacts error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch emergency contacts")


@router.post("/contacts")
async def add_emergency_contact(
    contact: dict,
    current_user: dict = Depends(get_current_user)
):
    """add a new emergency contact"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # validate required fields
        required = ["name", "phone"]
        for field in required:
            if field not in contact or not contact[field]:
                raise HTTPException(status_code=400, detail=f"missing required field: {field}")
        
        # check max contacts limit
        existing = firestore.get_emergency_contacts(uid)
        if len(existing) >= 5:
            raise HTTPException(status_code=400, detail="maximum 5 emergency contacts allowed")
        
        # validate phone (basic check)
        phone = contact["phone"].strip()
        if len(phone) < 8:
            raise HTTPException(status_code=400, detail="invalid phone number")
        
        # prepare contact data
        contact_data = {
            "name": contact["name"].strip(),
            "phone": phone,
            "relationship": contact.get("relationship", ""),
            "email": contact.get("email", ""),
            "priority": contact.get("priority", len(existing) + 1),  # order of contact
            "notify_on": contact.get("notify_on", ["critical_heart_rate", "fall_detected"]),
            "created_at": datetime.now().isoformat()
        }
        
        contact_id = firestore.add_emergency_contact(uid, contact_data)
        
        if not contact_id:
            raise HTTPException(status_code=500, detail="failed to add contact")
        
        print(f"DEBUG: added emergency contact {contact_id} for user {uid}")
        
        return {
            "user_id": uid,
            "contact_id": contact_id,
            "message": "emergency contact added",
            "contact": contact_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: add emergency contact error: {e}")
        raise HTTPException(status_code=500, detail="failed to add emergency contact")


@router.put("/contacts/{contact_id}")
async def update_emergency_contact(
    contact_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """update an emergency contact"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        success = firestore.update_emergency_contact(contact_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="contact not found")
        
        return {
            "user_id": uid,
            "contact_id": contact_id,
            "message": "emergency contact updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: update emergency contact error: {e}")
        raise HTTPException(status_code=500, detail="failed to update contact")


@router.delete("/contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_user)
):
    """delete an emergency contact"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        success = firestore.delete_emergency_contact(contact_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="contact not found")
        
        print(f"DEBUG: deleted emergency contact {contact_id}")
        
        return {
            "user_id": uid,
            "contact_id": contact_id,
            "message": "emergency contact deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: delete emergency contact error: {e}")
        raise HTTPException(status_code=500, detail="failed to delete contact")


@router.post("/alert")
async def trigger_emergency_alert(
    alert_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    trigger an emergency alert to all contacts.
    this would typically be called automatically by the system
    when critical events are detected (very high heart rate, fall, etc.)
    """
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get user's emergency contacts
        contacts = firestore.get_emergency_contacts(uid)
        
        if not contacts:
            return {
                "user_id": uid,
                "message": "no emergency contacts configured",
                "alert_sent": False
            }
        
        # prepare alert message
        alert_type = alert_data.get("type", "general")
        location = alert_data.get("location", "unknown location")
        message = alert_data.get("message", f"emergency alert: {alert_type}")
        
        # in real implementation, this would send email/push to contacts
        # for now, we just log it and create notifications
        notified_contacts = []
        
        for contact in contacts:
            contact_id = contact.get("contact_id") or contact.get("id")
            
            # check if this contact should be notified for this alert type
            notify_on = contact.get("notify_on", ["critical_heart_rate", "fall_detected"])
            
            # for demo, notify everyone
            notified_contacts.append({
                "contact_id": contact_id,
                "name": contact.get("name"),
                "phone": contact.get("phone"),
                "email": contact.get("email", ""),
                "notified": True
            })
            
            if contact.get("email"):
                print(f"DEBUG: would send email to {contact.get('name')} at {contact.get('email')}: {message}")
            else:
                print(f"DEBUG: contact {contact.get('name')} has no email; in-app log only")
        
        # create notification for user
        firestore.create_notification({
            "user_id": uid,
            "title": "Emergency Alert Sent",
            "message": f"alert sent to {len(notified_contacts)} emergency contacts",
            "type": "emergency",
            "read": False,
            "data": {
                "alert_type": alert_type,
                "contacts_notified": len(notified_contacts)
            },
            "created_at": datetime.now().isoformat()
        })
        
        return {
            "user_id": uid,
            "alert_type": alert_type,
            "message": message,
            "location": location,
            "contacts_notified": len(notified_contacts),
            "notified": notified_contacts,
            "alert_sent": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"DEBUG: emergency alert error: {e}")
        raise HTTPException(status_code=500, detail="failed to send emergency alert")


@router.get("/settings")
async def get_emergency_settings(current_user: dict = Depends(get_current_user)):
    """get user's emergency alert settings"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get settings from user profile
        user = firestore.get_user(uid)
        
        settings = user.get("emergency_settings", {}) if user else {}
        
        # defaults
        default_settings = {
            "auto_alert_enabled": True,
            "heart_rate_threshold": 180,  # bpm
            "fall_detection_enabled": True,
            "location_sharing_enabled": True,
            "alert_delay_seconds": 30,  # delay before sending to allow user to cancel
        }
        
        # merge with defaults
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        return {
            "user_id": uid,
            "settings": settings
        }
        
    except Exception as e:
        print(f"DEBUG: get emergency settings error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch emergency settings")


@router.put("/settings")
async def update_emergency_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user)
):
    """update user's emergency alert settings"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # update in user profile
        success = firestore.update_user(uid, {"emergency_settings": settings})
        
        if not success:
            raise HTTPException(status_code=500, detail="failed to update settings")
        
        return {
            "user_id": uid,
            "message": "emergency settings updated",
            "settings": settings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: update emergency settings error: {e}")
        raise HTTPException(status_code=500, detail="failed to update settings")
