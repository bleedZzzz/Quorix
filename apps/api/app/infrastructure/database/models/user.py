"""Quorix API — User database model."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """Application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    workspace_memberships: Mapped[list[WorkspaceMember]] = relationship(
        "WorkspaceMember", back_populates="user", lazy="selectin"
    )


# Import here to avoid circular — SQLAlchemy resolves string refs at mapper config time
from app.infrastructure.database.models.workspace import WorkspaceMember  # noqa: E402, F401
