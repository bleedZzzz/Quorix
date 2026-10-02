"""Systematic literature review and screening service."""

from __future__ import annotations

import uuid

from app.infrastructure.database.models.research import LiteratureReview, ReviewScreening
from app.infrastructure.repositories.research_repository import ResearchRepository


class ReviewService:
    """Orchestrates systematic literature review projects, screening protocols, and synthesis."""

    def __init__(self, research_repo: ResearchRepository) -> None:
        self.repo = research_repo

    async def create_review(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        research_question: str | None = None,
        scope: str | None = None,
        inclusion_criteria: str | None = None,
        exclusion_criteria: str | None = None,
    ) -> LiteratureReview:
        return await self.repo.create_review(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            research_question=research_question,
            scope=scope,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
        )

    async def get_review(
        self,
        review_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> LiteratureReview | None:
        return await self.repo.get_review(review_id, workspace_id)

    async def list_reviews(self, workspace_id: uuid.UUID) -> list[LiteratureReview]:
        return await self.repo.list_reviews(workspace_id)

    async def add_screening_candidate(
        self,
        review_id: uuid.UUID,
        paper_id: uuid.UUID,
        status: str = "candidate",
        reason: str | None = None,
    ) -> ReviewScreening:
        return await self.repo.add_screening(
            review_id=review_id,
            paper_id=paper_id,
            status=status,
            reason=reason,
        )

    async def update_screening(
        self,
        review_id: uuid.UUID,
        paper_id: uuid.UUID,
        status: str,
        reason: str | None = None,
    ) -> ReviewScreening | None:
        return await self.repo.update_screening_status(
            review_id=review_id,
            paper_id=paper_id,
            status=status,
            reason=reason,
        )
