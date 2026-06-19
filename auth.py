"""
auth.py — Password hashing + JWT token logic
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from bcrypt import hashpw, checkpw, gensalt

# ============================================================
# CONFIG
# Pull SECRET_KEY from .env in production.

# ============================================================

SECRET_KEY = "travelmind-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(plain_password: str) -> str:
    """Hash a plain password using bcrypt."""
    return hashpw(plain_password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against a stored bcrypt hash."""
    return checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ============================================================
# JWT TOKENS
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT token.
    data should include: {"sub": user_id, "email": email, "name": name}
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    Returns the payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================
# EXTRACT CURRENT USER FROM REQUEST COOKIE
# ============================================================

def get_current_user(request) -> Optional[dict]:
    """
    Read the JWT from the 'access_token' cookie and return user info.
    Returns dict with keys: id, email, name
    Returns None if not logged in or token is invalid.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    return decode_token(token)