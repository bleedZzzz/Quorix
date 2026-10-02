"""Research repository for relationships, gaps, reviews, and screening."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.research import (
    LiteratureReview,
    PaperRelationship,
    ResearchGap,
    ReviewScreening,
)


class ResearchRepository:
    """Repository handling research graph edges, gaps, systematic literature reviews, and screening."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Paper Relationships (Knowledge Graph)
    async def create_relationship(
        self,
        workspace_id: uuid.UUID,
        source_paper_id: uuid.UUID,
        target_paper_id: uuid.UUID,
        relationship_type: str,
        confidence: float | None = None,
        evidence_ids: list[uuid.UUID] | None = None,
    ) -> PaperRelationship:
        rel = PaperRelationship(
            workspace_id=workspace_id,
            source_paper_id=source_paper_id,
            target_paper_id=target_paper_id,
            relationship_type=relationship_type,
            confidence=confidence,
            evidence_ids=evidence_ids or [],
        )
        self.session.add(rel)
        await self.session.flush()
        return rel

    async def get_relationships(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID | None = None,
    ) -> list[PaperRelationship]:
        stmt = (
            select(PaperRelationship)
            .options(
                selectinload(PaperRelationship.source_paper),
                selectinload(PaperRelationship.target_paper),
            )
            .where(PaperRelationship.workspace_id == workspace_id)
        )
        if paper_id:
            stmt = stmt.where(
                (PaperRelationship.source_paper_id == paper_id)
                | (PaperRelationship.target_paper_id == paper_id)
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Research Gaps
    async def create_gap(
        self,
        workspace_id: uuid.UUID,
        gap_description: str,
        gap_type: str | None = None,
        confidence: float | None = None,
        why_detected: str | None = None,
        potential_direction: str | None = None,
        supporting_paper_ids: list[uuid.UUID] | None = None,
    ) -> ResearchGap:
        gap = ResearchGap(
            workspace_id=workspace_id,
            gap_description=gap_description,
            gap_type=gap_type,
            confidence=confidence,
            why_detected=why_detected,
            potential_direction=potential_direction,
            supporting_paper_ids=supporting_paper_ids or [],
        )
        self.session.add(gap)
        await self.session.flush()
        return gap

    async def list_gaps(self, workspace_id: uuid.UUID) -> list[ResearchGap]:
        stmt = (
            select(ResearchGap)
            .where(ResearchGap.workspace_id == workspace_id)
            .order_by(ResearchGap.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Systematic Literature Reviews
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
        review = LiteratureReview(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            research_question=research_question,
            scope=scope,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
        )
        self.session.add(review)
        await self.session.flush()
        return review

    async def get_review(
        self,
        review_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> LiteratureReview | None:
        stmt = (
            select(LiteratureReview)
            .options(
                selectinload(LiteratureReview.screenings).selectinload(ReviewScreening.paper),
            )
            .where(LiteratureReview.id == review_id, LiteratureReview.workspace_id == workspace_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_reviews(self, workspace_id: uuid.UUID) -> list[LiteratureReview]:
        stmt = (
            select(LiteratureReview)
            .where(LiteratureReview.workspace_id == workspace_id)
            .order_by(LiteratureReview.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_screening(
        self,
        review_id: uuid.UUID,
        paper_id: uuid.UUID,
        status: str = "candidate",
        reason: str | None = None,
    ) -> ReviewScreening:
        screening = ReviewScreening(
            review_id=review_id,
            paper_id=paper_id,
            status=status,
            reason=reason,
            screened_at=datetime.now(UTC) if status != "candidate" else None,
        )
        self.session.add(screening)
        await self.session.flush()
        return screening

    async def update_screening_status(
        self,
        review_id: uuid.UUID,
        paper_id: uuid.UUID,
        status: str,
        reason: str | None = None,
    ) -> ReviewScreening | None:
        stmt = select(ReviewScreening).where(
            ReviewScreening.review_id == review_id,
            ReviewScreening.paper_id == paper_id,
        )
        result = await self.session.execute(stmt)
        screening = result.scalars().first()
        if screening:
            screening.status = status
            screening.reason = reason
            screening.screened_at = datetime.now(UTC)
            await self.session.flush()
        return screening
