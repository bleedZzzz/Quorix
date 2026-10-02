"""Quorix API — Tag, PaperTag, Annotation, Note, and NoteLink models."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.document import Document
    from app.infrastructure.database.models.paper import Paper
    from app.infrastructure.database.models.user import User
    from app.infrastructure.database.models.workspace import Workspace


class Tag(Base, UUIDMixin):
    """User-defined tags within a workspace."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_workspace_tag_name"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), default="#6366f1", nullable=True)

    workspace: Mapped[Workspace] = relationship("Workspace")


class PaperTag(Base):
    """Junction between Paper and Tag."""

    __tablename__ = "paper_tags"

    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    paper: Mapped[Paper] = relationship("Paper")
    tag: Mapped[Tag] = relationship("Tag")


class Annotation(Base, UUIDMixin, TimestampMixin):
    """Highlight and note annotation placed directly on a document page."""

    __tablename__ = "annotations"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    highlight_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    annotation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), default="#facc15", nullable=True)
    position_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    document: Mapped[Document] = relationship("Document")
    user: Mapped[User] = relationship("User")


class Note(Base, UUIDMixin, TimestampMixin):
    """Markdown research note with bi-directional linking."""

    __tablename__ = "notes"

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
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    paper_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    folder: Mapped[str | None] = mapped_column(String(200), default="/", nullable=True)

    workspace: Mapped[Workspace] = relationship("Workspace")
    user: Mapped[User] = relationship("User")
    paper: Mapped[Paper | None] = relationship("Paper")


class NoteLink(Base):
    """Bi-directional backlink / reference between two notes."""

    __tablename__ = "note_links"

    source_note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    target_note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    link_type: Mapped[str] = mapped_column(String(50), default="reference", nullable=False)
