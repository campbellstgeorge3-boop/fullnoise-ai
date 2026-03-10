"""
Verify NextAuth JWT from Authorization: Bearer <token>.
NextAuth signs JWTs with NEXTAUTH_SECRET; we use the same secret to verify.
JWT payload should include: role ("admin" | "client"), and for clients: client_id.
"""
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import NEXTAUTH_SECRET

security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    """Decode and verify NextAuth JWT. Returns payload dict or raises 401."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            NEXTAUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_admin(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> dict:
    """Dependency: require role admin."""
    payload = verify_token(credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return payload


def require_client(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> dict:
    """Dependency: require role client and return payload with client_id."""
    payload = verify_token(credentials)
    if payload.get("role") != "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client access required")
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid client token")
    return payload
