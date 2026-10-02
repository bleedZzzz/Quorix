"""Quorix API — Paper repository for database operations on academic literature."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.paper import Author, Paper, PaperAuthor, PaperSource


class PaperRepository:
    """Repository handling CRUD and queries for papers, authors, and sources."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        workspace_id: uuid.UUID,
        title: str,
        abstract: str | None = None,
        year: int | None = None,
        venue: str | None = None,
        doi: str | None = None,
        arxiv_id: str | None = None,
        pdf_url: str | None = None,
        paper_type: str = "article",
        status: str = "imported",
        metadata: dict[str, Any] | None = None,
    ) -> Paper:
        paper = Paper(
            workspace_id=workspace_id,
            title=title,
            abstract=abstract,
            year=year,
            venue=venue,
            doi=doi,
            arxiv_id=arxiv_id,
            pdf_url=pdf_url,
            paper_type=paper_type,
            status=status,
            metadata_=metadata or {},
        )
        self.session.add(paper)
        await self.session.flush()
        return paper

    async def get_by_id(self, paper_id: uuid.UUID, workspace_id: uuid.UUID | None = None) -> Paper | None:
        stmt = (
            select(Paper)
            .options(
                selectinload(Paper.authors).selectinload(PaperAuthor.author),
                selectinload(Paper.sources),
                selectinload(Paper.documents),
            )
            .where(Paper.id == paper_id)
        )
        if workspace_id:
            stmt = stmt.where(Paper.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_doi(self, doi: str, workspace_id: uuid.UUID) -> Paper | None:
        stmt = select(Paper).where(Paper.doi == doi, Paper.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_arxiv(self, arxiv_id: str, workspace_id: uuid.UUID) -> Paper | None:
        stmt = select(Paper).where(Paper.arxiv_id == arxiv_id, Paper.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_papers(
        self,
        workspace_id: uuid.UUID,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Paper], int]:
        base_query = select(Paper).where(Paper.workspace_id == workspace_id)

        if status:
            base_query = base_query.where(Paper.status == status)

        if search:
            search_filter = or_(
                Paper.title.ilike(f"%{search}%"),
                Paper.abstract.ilike(f"%{search}%"),
                Paper.doi.ilike(f"%{search}%"),
                Paper.arxiv_id.ilike(f"%{search}%"),
            )
            base_query = base_query.where(search_filter)

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            base_query.options(
                selectinload(Paper.authors).selectinload(PaperAuthor.author),
                selectinload(Paper.sources),
            )
            .order_by(Paper.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def update_status(
        self,
        paper_id: uuid.UUID,
        status: str,
        metadata_update: dict[str, Any] | None = None,
    ) -> Paper | None:
        paper = await self.get_by_id(paper_id)
        if not paper:
            return None
        paper.status = status
        if metadata_update:
            paper.metadata_ = {**paper.metadata_, **metadata_update}
        await self.session.flush()
        return paper

    async def add_author(
        self,
        paper_id: uuid.UUID,
        name: str,
        affiliation: str | None = None,
        external_ids: dict[str, Any] | None = None,
        position: int = 0,
    ) -> Author:
        # Check if author exists or create
        stmt = select(Author).where(Author.name == name)
        result = await self.session.execute(stmt)
        author = result.scalars().first()

        if not author:
            author = Author(
                name=name,
                affiliation=affiliation,
                external_ids=external_ids or {},
            )
            self.session.add(author)
            await self.session.flush()

        paper_author = PaperAuthor(
            paper_id=paper_id,
            author_id=author.id,
            position=position,
        )
        self.session.add(paper_author)
        await self.session.flush()
        return author

    async def add_source(
        self,
        paper_id: uuid.UUID,
        source: str,
        external_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> PaperSource:
        paper_source = PaperSource(
            paper_id=paper_id,
            source=source,
            external_id=external_id,
            metadata_=metadata or {},
        )
        self.session.add(paper_source)
        await self.session.flush()
        return paper_source

    async def delete(self, paper_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        stmt = delete(Paper).where(Paper.id == paper_id, Paper.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
