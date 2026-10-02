"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import (
    AuthenticationError,
    AuthService,
    RegistrationError,
)
from app.config.settings import Settings, get_settings
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(),
    settings: Settings = Depends(get_settings),
) -> ApiResponse:
    """Register a new user account."""
    service = AuthService(session, settings)
    try:
        user, tokens = await service.register(request)
    except RegistrationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return ApiResponse(
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        }
    )


@router.post("/login", response_model=ApiResponse[dict])
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(),
    settings: Settings = Depends(get_settings),
) -> ApiResponse:
    """Authenticate and obtain tokens."""
    service = AuthService(session, settings)
    try:
        user, tokens = await service.login(request)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return ApiResponse(
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        }
    )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(),
    settings: Settings = Depends(get_settings),
) -> ApiResponse:
    """Refresh an access token using a valid refresh token."""
    from app.infrastructure.repositories.user_repository import UserRepository
    from app.security.tokens import TokenError, decode_token

    try:
        payload = decode_token(request.refresh_token, settings)
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
        )

    from uuid import UUID
    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    service = AuthService(session, settings)
    tokens = await service.refresh(user)
    return ApiResponse(data=tokens)
