"""Authentication service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.security.password import hash_password, verify_password
from app.security.tokens import create_access_token, create_refresh_token


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class RegistrationError(Exception):
    """Raised when registration fails."""


class AuthService:
    """Application service for authentication workflows."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._repo = UserRepository(session)
        self._settings = settings

    async def register(self, request: RegisterRequest) -> tuple[User, TokenResponse]:
        """Register a new user and return user + tokens."""
        if await self._repo.email_exists(request.email):
            raise RegistrationError("Email already registered")

        user = User(
            email=request.email.lower(),
            password_hash=hash_password(request.password),
            display_name=request.display_name,
        )
        user = await self._repo.create(user)

        tokens = self._create_tokens(user)
        return user, tokens

    async def login(self, request: LoginRequest) -> tuple[User, TokenResponse]:
        """Authenticate a user and return user + tokens."""
        user = await self._repo.get_by_email(request.email)
        if user is None or not verify_password(request.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        tokens = self._create_tokens(user)
        return user, tokens

    async def refresh(self, user: User) -> TokenResponse:
        """Generate new tokens for an authenticated user."""
        return self._create_tokens(user)

    def _create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh token pair."""
        return TokenResponse(
            access_token=create_access_token(user.id, self._settings),
            refresh_token=create_refresh_token(user.id, self._settings),
        )
