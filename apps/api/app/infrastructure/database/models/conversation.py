"""Conversation and Message models."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.evidence import Claim
    from app.infrastructure.database.models.user import User
    from app.infrastructure.database.models.workspace import Workspace


class Conversation(Base, UUIDMixin, TimestampMixin):
    """Interactive research conversation session."""

    __tablename__ = "conversations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), default="New Research Session", nullable=False)
    scope_type: Mapped[str] = mapped_column(
        String(50),
        default="workspace",
        nullable=False,
    )  # workspace, project, paper, multi_paper
    scope_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        default=list,
        nullable=False,
    )  # paper_ids or project_id

    # Relationships
    workspace: Mapped[Workspace] = relationship("Workspace")
    user: Mapped[User] = relationship("User")
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base, UUIDMixin, TimestampMixin):
    """Individual message in a research conversation."""

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
    claims: Mapped[list[Claim]] = relationship(
        "Claim",
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="Claim.order_index",
    )
