"""
auth.py — JWT-based authentication utilities for RBAC.

Roles:
  administrator        — full CRUD access to patients, encounters, analytics, user management
  clinical_operations  — read + create + edit patients/encounters; no delete
  analyst              — analytics endpoints only; no patient or encounter data
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import database
import models

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# ── JWT config ────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-healthcare-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

import bcrypt as _bcrypt

# ── OAuth2 token URL ──────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Valid roles ───────────────────────────────────────────────────────────────
VALID_ROLES = ("administrator", "clinical_operations", "analyst")

# ── Password hashing (raw bcrypt, compatible with bcrypt 5.x) ────────────────
def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── Current-user dependency ───────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# ── Role-guard factories ───────────────────────────────────────────────────────
def require_roles(*roles: str):
    """Return a FastAPI dependency that enforces one of the given roles."""
    def _guard(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}.",
            )
        return current_user
    return _guard


# Pre-built guards used in routes
require_administrator   = require_roles("administrator")
require_clinical_ops    = require_roles("administrator", "clinical_operations")
require_any             = require_roles("administrator", "clinical_operations", "analyst")
require_patient_access  = require_roles("administrator", "clinical_operations")   # analyst excluded
