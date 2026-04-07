#!/usr/bin/env python3
"""appointments and reminders for provider visits"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, public_role, require_role
from app.routers.notifications import create_notification_internal

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/")
async def list_my_appointments(current_user: dict = Depends(get_current_user)):
    """list appointments for the current user (patient or provider)"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        role = current_user.get("role", "user")
        appointments = firestore.get_appointments_for_user(uid, role=role)
        return {
            "user_id": uid,
            "role": public_role(role),
            "appointments": appointments,
            "count": len(appointments)
        }
    except Exception as e:
        print(f"DEBUG: list appointments error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch appointments")


@router.post("/")
async def create_appointment(
    payload: dict,
    current_user: dict = Depends(require_role("healthcare_provider"))
):
    """
    create an appointment and reminder for a patient.
    providers call this to schedule; patient_id is required.
    """
    from app.core import firestore
    
    try:
        provider_id = current_user["uid"]
        patient_id = payload.get("patient_id")
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id is required")
        
        scheduled_for = payload.get("scheduled_for")
        if not scheduled_for:
            raise HTTPException(status_code=400, detail="scheduled_for datetime is required")
        
        reminder_minutes_before = payload.get("reminder_minutes_before", 60)
        
        appointment = {
            "patient_id": patient_id,
            "provider_id": provider_id,
            "scheduled_for": scheduled_for,
            "note": payload.get("note", ""),
            "reminder_minutes_before": reminder_minutes_before,
            "status": payload.get("status", "scheduled")
        }
        
        appt_id = firestore.create_appointment(appointment)
        if not appt_id:
            raise HTTPException(status_code=500, detail="failed to create appointment")
        
        # create in app reminder notification for the patient
        reminder_msg = f"Appointment scheduled with your provider at {scheduled_for}"
        create_notification_internal(
            user_id=patient_id,
            title="Appointment Reminder",
            message=reminder_msg,
            notification_type="appointment",
            data={
                "appointment_id": appt_id,
                "scheduled_for": scheduled_for,
                "provider_id": provider_id,
                "reminder_minutes_before": reminder_minutes_before
            }
        )
        
        return {
            "appointment_id": appt_id,
            "message": "appointment created",
            "appointment": appointment
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: create appointment error: {e}")
        raise HTTPException(status_code=500, detail="failed to create appointment")


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    updates: dict,
    current_user: dict = Depends(require_role("healthcare_provider"))
):
    """update appointment details/status"""
    from app.core import firestore
    
    try:
        success = firestore.update_appointment(appointment_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="appointment not found")
        return {"appointment_id": appointment_id, "message": "appointment updated"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: update appointment error: {e}")
        raise HTTPException(status_code=500, detail="failed to update appointment")
