from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin.auth as firebase_auth
import os
from typing import Optional

security = HTTPBearer(auto_error=False)

# check if in mock mode
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
CHECK_REVOKED = os.getenv("CHECK_REVOKED_TOKENS", "false").lower() == "true"
ROLE_ALIASES = {
    "professional": "healthcare_provider",
    "healthcare_provider": "healthcare_provider",
    "provider": "healthcare_provider",
    "user": "user",
}


def normalize_role(role: Optional[str]) -> str:
    return ROLE_ALIASES.get((role or "user").strip().lower(), role or "user")


async def verify_firebase_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    if not credentials and not request.cookies.get("session"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        if credentials:
            token = credentials.credentials

            # mock mode accepts any token starting with "mock_"
            if USE_MOCK and token.startswith("mock_"):
                # check if it's a provider token
                if "provider" in token.lower():
                    return {
                        "uid": "provider456",
                        "email": "dr.smith@hospital.com",
                        "role": "healthcare_provider"
                    }
                return {
                    "uid": "user123",
                    "email": "test@pulselink.com",
                    "role": "user"
                }

            decoded_token = firebase_auth.verify_id_token(token, check_revoked=CHECK_REVOKED)
        else:
            session_cookie = request.cookies.get("session", "")
            decoded_token = firebase_auth.verify_session_cookie(session_cookie, check_revoked=CHECK_REVOKED)
        return decoded_token
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.UserDisabledError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(request: Request, token: dict = Depends(verify_firebase_token)):
    mfa_verified = False
    password_expired = False
    role = token.get("role")
    try:
        from app.core import firestore
        mfa_status = firestore.get_mfa_status(token.get("uid"))
        mfa_verified = mfa_status.get("verified", False)
        password_status = firestore.get_password_status(token.get("uid"))
        password_expired = password_status.get("expired", False)
        if not role:
            user = firestore.get_user(token.get("uid")) or {}
            role = user.get("role")
    except Exception:
        mfa_verified = False
        password_expired = False
        role = token.get("role")

    allowed_when_expired = [
        "/api/v1/auth/me",
        "/api/v1/auth/change-password",
        "/api/v1/auth/logout",
        "/api/v1/auth/session-logout",
        "/api/v1/auth/mfa",
    ]
    if password_expired and not any(request.url.path.startswith(path) for path in allowed_when_expired):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password expired. Please change your password.",
        )

    return {
        "uid": token.get("uid"),
        "email": token.get("email"),
        "role": normalize_role(role),
        "mfa_verified": mfa_verified,
        "password_expired": password_expired,
    }


def require_role(required_role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if normalize_role(current_user["role"]) != normalize_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Need {required_role} role",
            )
        return current_user

    return role_checker


def require_mfa():
    async def mfa_checker(current_user: dict = Depends(get_current_user)):
        if not current_user.get("mfa_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA verification required",
            )
        return current_user

    return mfa_checker
