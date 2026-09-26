"""
KlartX — JWT auth, password hashing, role middleware
Contract ID: @auth/roles
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.database import SessionLocal, get_session

ALGORITHM = "HS256"


def _load_signing_key() -> str:
    """JWT signing key, never in the source (a key in a public repo lets anyone forge tokens).

    KLARTX_SECRET_KEY env wins. On vm106 (systemd sets STATE_DIRECTORY) a random key is created
    once in the writable state dir and reused, so tokens survive restarts. Local runs get a fresh
    random key per process.
    """
    from_env = os.environ.get("KLARTX_SECRET_KEY", "")
    if from_env:
        return from_env
    state_dir = os.environ.get("STATE_DIRECTORY", "").split(":")[0]
    if not state_dir:
        return secrets.token_urlsafe(48)
    key_file = Path(state_dir) / "jwt-signing-key"
    if not key_file.exists():
        fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(secrets.token_urlsafe(48))
    return key_file.read_text().strip()


SECRET_KEY = _load_signing_key()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class User:
    """Simple in-memory user for throwaway app."""
    def __init__(self, username: str, hashed_password: str, role: str = "user"):
        self.username = username
        self.hashed_password = hashed_password
        self.role = role  # user | admin | librarian


# In-memory user store (throwaway — no DB for users yet)
users: dict[str, User] = {
    "admin": User("admin", "hashed_admin", "admin"),
    "user": User("user", "hashed_user", "user"),
    "librarian": User("librarian", "hashed_librarian", "librarian"),
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify JWT token. Returns payload or raises."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
) -> User:
    """Extract and validate the current user from the Bearer token."""
    token = credentials.credentials
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = users.get(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(required_role: str):
    """Return a dependency that checks if the current user has the required role."""
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user
    return _checker
