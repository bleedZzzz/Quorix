"""Quorix API — Paper application service."""

from __future__ import annotations

import uuid

from app.infrastructure.database.models.paper import Paper
from app.infrastructure.repositories.paper_repository import PaperRepository
from app.schemas.paper import (
    PaperCreateRequest,
    PaperUpdateRequest,
)


class PaperService:
    """Service orchestrating academic paper operations."""

    def __init__(self, paper_repo: PaperRepository) -> None:
        self.repo = paper_repo

    async def create_paper(
        self,
        workspace_id: uuid.UUID,
        request: PaperCreateRequest,
    ) -> Paper:
        paper = await self.repo.create(
            workspace_id=workspace_id,
            title=request.title,
            abstract=request.abstract,
            year=request.year,
            venue=request.venue,
            doi=request.doi,
            arxiv_id=request.arxiv_id,
            pdf_url=request.pdf_url,
            paper_type=request.paper_type,
            status="imported",
            metadata=request.metadata,
        )

        for pos, auth in enumerate(request.authors):
            await self.repo.add_author(
                paper_id=paper.id,
                name=auth.name,
                affiliation=auth.affiliation,
                external_ids=auth.external_ids,
                position=pos,
            )

        for src in request.sources:
            await self.repo.add_source(
                paper_id=paper.id,
                source=src.source,
                external_id=src.external_id,
                metadata=src.metadata,
            )

        return await self.repo.get_by_id(paper.id, workspace_id)  # type: ignore

    async def get_paper(
        self,
        paper_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> Paper | None:
        return await self.repo.get_by_id(paper_id, workspace_id)

    async def list_papers(
        self,
        workspace_id: uuid.UUID,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Paper], int]:
        return await self.repo.list_papers(
            workspace_id=workspace_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def update_paper(
        self,
        paper_id: uuid.UUID,
        workspace_id: uuid.UUID,
        request: PaperUpdateRequest,
    ) -> Paper | None:
        paper = await self.repo.get_by_id(paper_id, workspace_id)
        if not paper:
            return None

        if request.title:
            paper.title = request.title
        if request.abstract is not None:
            paper.abstract = request.abstract
        if request.year is not None:
            paper.year = request.year
        if request.venue is not None:
            paper.venue = request.venue
        if request.doi is not None:
            paper.doi = request.doi
        if request.arxiv_id is not None:
            paper.arxiv_id = request.arxiv_id
        if request.status is not None:
            paper.status = request.status
        if request.metadata is not None:
            paper.metadata_ = {**paper.metadata_, **request.metadata}

        await self.repo.session.flush()
        return await self.repo.get_by_id(paper_id, workspace_id)

    async def delete_paper(self, paper_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        return await self.repo.delete(paper_id, workspace_id)
