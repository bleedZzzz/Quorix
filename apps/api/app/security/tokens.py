"""JWT token management."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app.config.settings import Settings


class TokenError(Exception):
    """Raised when token creation or validation fails."""


def create_access_token(user_id: UUID, settings: Settings, email: str | None = None) -> str:
    """Create a short-lived access token."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    if email:
        payload["email"] = email
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID, settings: Settings) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_token_pair(user_id: UUID, settings: Settings, email: str | None = None) -> dict[str, str]:
    """Create both access and refresh tokens."""
    return {
        "access_token": create_access_token(user_id, settings, email),
        "refresh_token": create_refresh_token(user_id, settings),
        "token_type": "bearer",
    }


def decode_token(token: str, settings: Settings) -> dict:
    """Decode and validate a JWT token. Raises TokenError on failure."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if "sub" not in payload:
            raise TokenError("Token missing subject claim")
        return payload
    except JWTError as e:
        raise TokenError(f"Invalid token: {e}") from e
