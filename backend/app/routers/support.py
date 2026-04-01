#!/usr/bin/env python3
"""support and help/faq endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, require_mfa, require_role

router = APIRouter(prefix="/support", tags=["support"])


@router.post("/tickets")
async def create_ticket(
    payload: dict,
    current_user: dict = Depends(get_current_user)
):
    """create a support/help ticket"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        subject = payload.get("subject", "").strip()
        message = payload.get("message", "").strip()
        
        if not subject:
            raise HTTPException(status_code=400, detail="subject is required")
        if not message:
            raise HTTPException(status_code=400, detail="message is required")
        
        ticket = {
            "subject": subject,
            "message": message,
            "category": payload.get("category", "general"),
            "status": "open",
            "created_at": datetime.now().isoformat()
        }
        
        ticket_id = firestore.create_support_ticket(uid, ticket)
        if not ticket_id:
            raise HTTPException(status_code=500, detail="failed to create ticket")
        
        return {
            "user_id": uid,
            "ticket_id": ticket_id,
            "message": "ticket submitted",
            "ticket": ticket
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: create ticket error: {e}")
        raise HTTPException(status_code=500, detail="failed to submit ticket")


@router.get("/tickets")
async def list_tickets(current_user: dict = Depends(get_current_user)):
    """list support tickets for current user"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        tickets = firestore.get_support_tickets(uid)
        return {
            "user_id": uid,
            "tickets": tickets,
            "count": len(tickets)
        }
    except Exception as e:
        print(f"DEBUG: list tickets error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch tickets")


@router.get("/system-status")
async def get_system_status(current_user: dict = Depends(require_role("healthcare_provider"))):
    from app.core.backup import list_backups

    try:
        backups = list_backups()
        return {
            "server_time": datetime.now().isoformat(),
            "backup_count": len(backups),
            "latest_backup": backups[0] if backups else None,
        }
    except Exception as e:
        print(f"DEBUG: system status error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch system status")


@router.get("/backups")
async def get_backups(current_user: dict = Depends(require_role("healthcare_provider"))):
    from app.core.backup import list_backups

    try:
        backups = list_backups()
        return {
            "count": len(backups),
            "backups": backups,
        }
    except Exception as e:
        print(f"DEBUG: list backups error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch backups")


@router.post("/backups/run")
async def run_backup(current_user: dict = Depends(require_mfa())):
    from app.core import firestore
    from app.core.backup import create_backup_snapshot

    try:
        if current_user.get("role") != "healthcare_provider":
            raise HTTPException(status_code=403, detail="provider role required")

        result = create_backup_snapshot()
        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="create_backup",
            category="security",
            status="success",
            details={"filename": result["filename"]},
        )

        return {
            "message": "backup created",
            "backup": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: run backup error: {e}")
        raise HTTPException(status_code=500, detail="failed to create backup")
