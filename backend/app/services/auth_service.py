"""
SceneForge AI - Authentication & Cryptography Service
Handles password hashing and JWT token lifecycle.
"""

import os
import time
import base64
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from backend.app.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_password_hash(password: str) -> str:
    """Hashes a password securely using native bcrypt."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except Exception:
        salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"sha256${salt}${digest}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            import bcrypt
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        elif hashed_password.startswith("sha256$"):
            _, salt, digest = hashed_password.split("$")
            computed = hashlib.sha256((salt + plain_password).encode()).hexdigest()
            return hmac.compare_digest(digest, computed)
        return False
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})

    try:
        from jose import jwt
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception:
        # Standard HMAC-SHA256 JWT implementation fallback
        header = {"alg": "HS256", "typ": "JWT"}
        def b64_encode(d):
            return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
        hdr_b64 = b64_encode(header)
        payload_b64 = b64_encode(to_encode)
        msg = f"{hdr_b64}.{payload_b64}".encode()
        sig = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{hdr_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT access token."""
    try:
        from jose import jwt
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            hdr_b64, payload_b64, sig_b64 = parts
            msg = f"{hdr_b64}.{payload_b64}".encode()
            expected_sig = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest()
            def b64_decode(s):
                pad = len(s) % 4
                if pad:
                    s += "=" * (4 - pad)
                return base64.urlsafe_b64decode(s)
            actual_sig = b64_decode(sig_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None
            payload = json.loads(b64_decode(payload_b64).decode())
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None
