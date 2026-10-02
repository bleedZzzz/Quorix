"""Quorix API — Paper, Author, and PaperSource models."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.document import Document
    from app.infrastructure.database.models.workspace import Workspace


class Paper(Base, UUIDMixin, TimestampMixin):
    """Academic paper entity."""

    __tablename__ = "papers"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    arxiv_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="imported",
        nullable=False,
    )  # imported, ingesting, ready, failed
    paper_type: Mapped[str | None] = mapped_column(
        String(50),
        default="article",
        nullable=True,
    )  # article, preprint, report, thesis, etc.
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    # Relationships
    workspace: Mapped[Workspace] = relationship("Workspace", back_populates="papers")
    authors: Mapped[list[PaperAuthor]] = relationship(
        "PaperAuthor",
        back_populates="paper",
        cascade="all, delete-orphan",
        order_by="PaperAuthor.position",
    )
    sources: Mapped[list[PaperSource]] = relationship(
        "PaperSource",
        back_populates="paper",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class Author(Base, UUIDMixin):
    """Academic author entity."""

    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    affiliation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_ids: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    paper_associations: Mapped[list[PaperAuthor]] = relationship(
        "PaperAuthor",
        back_populates="author",
        cascade="all, delete-orphan",
    )


class PaperAuthor(Base):
    """Junction model connecting papers and authors with position ordering."""

    __tablename__ = "paper_authors"

    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    paper: Mapped[Paper] = relationship("Paper", back_populates="authors")
    author: Mapped[Author] = relationship("Author", back_populates="paper_associations")


class PaperSource(Base, UUIDMixin):
    """External source identifiers and origins (arXiv, OpenAlex, Semantic Scholar, Crossref)."""

    __tablename__ = "paper_sources"
    __table_args__ = (
        UniqueConstraint("paper_id", "source", name="uq_paper_source"),
    )

    paper_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # arxiv, openalex, crossref, semantic_scholar
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
    )

    paper: Mapped[Paper] = relationship("Paper", back_populates="sources")
