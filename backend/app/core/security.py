from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin.auth as firebase_auth
import os

security = HTTPBearer()

# check if in mock mode
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"


async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials

    # mock mode - accept any token starting with "mock_"
    if USE_MOCK and token.startswith("mock_"):
        return {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user"
        }

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        # invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Bad token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: dict = Depends(verify_firebase_token)):
    return {
        "uid": token.get("uid"),
        "email": token.get("email"),
        "role": token.get("role", "user"),
    }


def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Need {required_role} role",
            )
        return current_user

    return role_checker
