"""Quorix API — Authentication Pydantic schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


RefreshTokenRequest = RefreshRequest


class UserResponse(BaseModel):
    """Public user representation."""
    id: UUID
    email: str
    display_name: str | None
    avatar_url: str | None

    model_config = {"from_attributes": True}
