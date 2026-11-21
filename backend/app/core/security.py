"""HER AI — Cryptographic Security & Authentication Utilities.

Provides:
  - Argon2id secure password hashing and verification (OWASP recommended parameters).
  - JWT Access Token issuance and validation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import argon2
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings

logger = logging.getLogger(__name__)

# OWASP Recommended Parameters for Argon2id:
# - memory_cost: 65536 KiB (64 MiB)
# - time_cost: 2 iterations
# - parallelism: 1 thread
# - hash_len: 32 bytes
# - type: Argon2id
_password_hasher = argon2.PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    type=argon2.Type.ID,
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    if not password:
        raise ValueError("Password cannot be empty.")
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2id hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(
    subject: str,
    claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if claims:
        payload.update(claims)

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a signed JWT access token.
    Raises:
        ExpiredSignatureError: If the token has expired.
        InvalidTokenError: If the token is invalid or tampered with.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

