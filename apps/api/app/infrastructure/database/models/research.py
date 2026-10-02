"""PaperRelationship, ResearchGap, LiteratureReview, and ReviewScreening models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.paper import Paper
    from app.infrastructure.database.models.user import User
    from app.infrastructure.database.models.workspace import Workspace


class PaperRelationship(Base, UUIDMixin):
    """Semantic or citation edge between papers in the research graph."""

    __tablename__ = "paper_relationships"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(
        "relationship",
        String(50),
        nullable=False,
    )  # cites, cited_by, builds_on, extends, contradicts, supports, similar_to
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        default=list,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )

    source_paper: Mapped[Paper] = relationship("Paper", foreign_keys=[source_paper_id])
    target_paper: Mapped[Paper] = relationship("Paper", foreign_keys=[target_paper_id])


class ResearchGap(Base, UUIDMixin):
    """Detected contradiction, unexplored angle, or limitation across literature."""

    __tablename__ = "research_gaps"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gap_description: Mapped[str] = mapped_column(Text, nullable=False)
    gap_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # methodological, empirical, theoretical
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    why_detected: Mapped[str | None] = mapped_column(Text, nullable=True)
    potential_direction: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_paper_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        default=list,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )

    workspace: Mapped[Workspace] = relationship("Workspace")


class LiteratureReview(Base, UUIDMixin, TimestampMixin):
    """Systematic literature review project with screening protocol."""

    __tablename__ = "literature_reviews"

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
    research_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    inclusion_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    exclusion_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    synthesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )  # draft, in_progress, completed

    workspace: Mapped[Workspace] = relationship("Workspace")
    user: Mapped[User] = relationship("User")
    screenings: Mapped[list[ReviewScreening]] = relationship(
        "ReviewScreening",
        back_populates="review",
        cascade="all, delete-orphan",
    )


class ReviewScreening(Base, UUIDMixin):
    """Paper screening status within a systematic literature review."""

    __tablename__ = "review_screening"
    __table_args__ = (
        UniqueConstraint("review_id", "paper_id", name="uq_review_paper_screening"),
    )

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("literature_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="candidate",
        nullable=False,
    )  # candidate, screening, included, excluded, needs_review
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    screened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    review: Mapped[LiteratureReview] = relationship("LiteratureReview", back_populates="screenings")
    paper: Mapped[Paper] = relationship("Paper")
