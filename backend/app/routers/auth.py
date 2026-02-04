from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from pydantic import BaseModel, EmailStr
import sys
import os
import firebase_admin.auth as firebase_auth

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    oob_code: str  # out-of-band code from Firebase email
    new_password: str


@router.get("/me")
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


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # TODO: add rate limiting so people dont spam this
    try:
        link = firebase_auth.generate_password_reset_link(request.email)
        
        # firebase handles the email sending
        # dont return the link (security)
        return {
            "message": "Password reset email sent",
            "email": request.email
        }
    except firebase_auth.UserNotFoundError:
        # dont tell if email exists (security thing)
        return {
            "message": "If this email exists, a reset link has been sent",
            "email": request.email
        }
    except Exception as e:
        print(f"DEBUG: forgot password error: {e}")  # TODO: remove this
        raise HTTPException(
            status_code=500,
            detail="something went wrong"
        )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # verify reset code and update password
    # usually done by Firebase client SDK but added here just in case
    try:
        # check the code first
        decoded = firebase_auth.verify_password_reset_code(request.oob_code)
        email = decoded.get("email")
        
        # actually reset the password
        firebase_auth.confirm_password_reset(request.oob_code, request.new_password)
        
        return {
            "message": "Password reset successful",
            "email": email
        }
    except firebase_auth.InvalidArgumentError:
        raise HTTPException(
            status_code=400,
            detail="bad reset code"
        )
    except Exception as e:
        print(f"reset error: {e}")  # debug
        raise HTTPException(
            status_code=500,
            detail=f"failed: {str(e)[:50]}"  # truncate error
        )


@router.post("/change-password")
async def change_password(
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    # change password for logged in user
    try:
        firebase_auth.update_user(
            current_user["uid"],
            password=new_password
        )
        return {
            "message": "Password updated successfully",
            "user_id": current_user["uid"]
        }
    except Exception as e:
        # TODO: handle different error types
        raise HTTPException(
            status_code=500,
            detail="update failed"
        )
