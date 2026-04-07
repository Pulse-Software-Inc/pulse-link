from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from typing import Dict
from pydantic import BaseModel
import sys
import os
import random
import secrets
import time
from datetime import datetime, timedelta
import firebase_admin.auth as firebase_auth

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, public_role, serialize_public_role_fields
from app.routers.notifications import create_notification_internal

router = APIRouter(prefix="/auth", tags=["authentication"])
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session")
SESSION_DAYS = int(os.getenv("SESSION_COOKIE_DAYS", "5"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    oob_code: str  # out of band code from Firebase email
    new_password: str


class MFAVerifyRequest(BaseModel):
    code: str


class SessionLoginRequest(BaseModel):
    id_token: str
    csrf_token: str


def check_password_rules(password: str) -> str:
    if len(password) < 8:
        return "password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return "password must have an uppercase letter"
    if not any(c.islower() for c in password):
        return "password must have a lowercase letter"
    if not any(c.isdigit() for c in password):
        return "password must have a number"
    return ""


def set_session_cookie(response: Response, session_cookie: str):
    max_age = SESSION_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_cookie,
        max_age=max_age,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response):
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )


@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": public_role(current_user["role"]),
        "mfa_verified": current_user.get("mfa_verified", False),
        "password_expired": current_user.get("password_expired", False),
        "message": "Authentication successful"
    }


@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    return {"status": "valid", "user": serialize_public_role_fields(current_user)}


@router.get("/csrf")
async def get_csrf_token():
    token = secrets.token_urlsafe(24)
    response = JSONResponse({
        "csrf_token": token
    })
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return response


@router.post("/session-login")
async def session_login(
    payload: SessionLoginRequest,
    csrf_cookie: str = Cookie(default="", alias="csrf_token")
):
    from app.core import firestore

    if not csrf_cookie or csrf_cookie != payload.csrf_token:
        firestore.create_audit_log(
            user_id=None,
            action="session_login",
            category="security",
            status="failed",
            details={"reason": "csrf_failed"},
        )
        raise HTTPException(status_code=401, detail="bad csrf token")

    try:
        decoded = firebase_auth.verify_id_token(payload.id_token, check_revoked=True)
        auth_time = decoded.get("auth_time", 0)
        if time.time() - auth_time > 300:
            firestore.create_audit_log(
                user_id=decoded.get("uid"),
                action="session_login",
                category="security",
                status="failed",
                details={"reason": "recent_login_required"},
            )
            raise HTTPException(status_code=401, detail="recent login required")

        expires_in = timedelta(days=SESSION_DAYS)
        session_cookie = firebase_auth.create_session_cookie(payload.id_token, expires_in=expires_in)

        firestore.create_audit_log(
            user_id=decoded.get("uid"),
            action="session_login",
            category="security",
            status="success",
            details={"mode": "cookie"},
        )

        response = JSONResponse({
            "message": "session cookie created",
            "user_id": decoded.get("uid"),
        })
        set_session_cookie(response, session_cookie)
        return response
    except HTTPException:
        raise
    except Exception as e:
        firestore.create_audit_log(
            user_id=None,
            action="session_login",
            category="security",
            status="failed",
            details={"reason": "invalid_id_token"},
        )
        print(f"session login error: {e}")
        raise HTTPException(status_code=401, detail="failed to create session")


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    try:
        firestore.clear_mfa_state(current_user["uid"])

        if os.getenv("USE_MOCK", "false").lower() != "true":
            firebase_auth.revoke_refresh_tokens(current_user["uid"])

        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="logout",
            category="security",
            status="success",
        )

        response = JSONResponse({
            "message": "Logged out successfully",
            "user_id": current_user["uid"]
        })
        clear_session_cookie(response)
        return response
    except Exception as e:
        print(f"logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail="logout failed"
        )


@router.post("/session-logout")
async def session_logout(current_user: dict = Depends(get_current_user)):
    return await logout(current_user)


@router.post("/mfa/request")
async def request_mfa_code(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    try:
        code = str(random.randint(100000, 999999))
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        user = firestore.get_user(current_user["uid"]) or {}
        delivery_method = user.get("mfa_delivery_method", os.getenv("MFA_DELIVERY_MODE", "in_app"))
        saved = firestore.save_mfa_code(current_user["uid"], code, expires_at, delivery_method=delivery_method)

        if not saved:
            raise HTTPException(status_code=500, detail="failed to create mfa code")

        if delivery_method == "in_app":
            create_notification_internal(
                user_id=current_user["uid"],
                title="Your PulseLink code",
                message=f"Your verification code is {code}",
                notification_type="security",
                data={"kind": "mfa"}
            )

        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="mfa_request",
            category="security",
            status="success",
            details={"delivery_method": delivery_method},
        )

        response = {
            "message": "MFA code created",
            "user_id": current_user["uid"],
            "expires_at": expires_at,
            "delivery": delivery_method
        }
        if os.getenv("USE_MOCK", "false").lower() == "true" or os.getenv("EXPOSE_MFA_CODE", "false").lower() == "true":
            response["code"] = code

        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"mfa request error: {e}")
        raise HTTPException(
            status_code=500,
            detail="mfa request failed"
        )


@router.post("/mfa/verify")
async def verify_mfa_code(
    request: MFAVerifyRequest,
    current_user: dict = Depends(get_current_user)
):
    from app.core import firestore

    try:
        valid = firestore.verify_mfa_code(current_user["uid"], request.code)
        if not valid:
            firestore.create_audit_log(
                user_id=current_user["uid"],
                action="mfa_verify",
                category="security",
                status="failed",
            )
            raise HTTPException(status_code=400, detail="invalid or expired mfa code")

        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="mfa_verify",
            category="security",
            status="success",
        )

        return {
            "message": "MFA verified",
            "user_id": current_user["uid"],
            "verified": True
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"mfa verify error: {e}")
        raise HTTPException(
            status_code=500,
            detail="mfa verify failed"
        )


@router.get("/mfa/status")
async def get_mfa_status(current_user: dict = Depends(get_current_user)):
    from app.core import firestore

    try:
        status_data = firestore.get_mfa_status(current_user["uid"])
        return {
            "user_id": current_user["uid"],
            "mfa": status_data
        }
    except Exception as e:
        print(f"mfa status error: {e}")
        raise HTTPException(
            status_code=500,
            detail="failed to fetch mfa status"
        )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
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
        print(f"DEBUG: forgot password error: {e}")
        raise HTTPException(
            status_code=500,
            detail="something went wrong"
        )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # verify reset code and update password
    # usually done by Firebase client SDK but added here just in case
    from app.core import firestore

    try:
        password_error = check_password_rules(request.new_password)
        if password_error:
            raise HTTPException(status_code=400, detail=password_error)

        # check the code first
        decoded = firebase_auth.verify_password_reset_code(request.oob_code)
        email = decoded.get("email")
        
        # actually reset the password
        firebase_auth.confirm_password_reset(request.oob_code, request.new_password)
        if os.getenv("USE_MOCK", "false").lower() != "true":
            user = firebase_auth.get_user_by_email(email)
            firestore.mark_password_changed(user.uid)

        firestore.create_audit_log(
            user_id=None,
            action="reset_password",
            category="security",
            status="success",
            details={"email": email},
        )
        
        return {
            "message": "Password reset successful",
            "email": email
        }
    except HTTPException:
        raise
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
    from app.core import firestore
    try:
        password_error = check_password_rules(new_password)
        if password_error:
            raise HTTPException(status_code=400, detail=password_error)

        firebase_auth.update_user(
            current_user["uid"],
            password=new_password
        )
        if os.getenv("USE_MOCK", "false").lower() != "true":
            firebase_auth.revoke_refresh_tokens(current_user["uid"])
        firestore.mark_password_changed(current_user["uid"])
        firestore.create_audit_log(
            user_id=current_user["uid"],
            action="change_password",
            category="security",
            status="success",
        )
        return {
            "message": "Password updated successfully",
            "user_id": current_user["uid"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="update failed"
        )
