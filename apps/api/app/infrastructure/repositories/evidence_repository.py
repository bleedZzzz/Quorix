"""Quorix API — Evidence repository for claims, evidence spans, and citations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.evidence import Citation, Claim, EvidenceSpan


class EvidenceRepository:
    """Repository handling CRUD and queries for claims, evidence spans, and citations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_claim(
        self,
        message_id: uuid.UUID,
        claim_text: str,
        verification_state: str = "unverified",
        confidence: float | None = None,
        order_index: int = 0,
    ) -> Claim:
        claim = Claim(
            message_id=message_id,
            claim_text=claim_text,
            verification_state=verification_state,
            confidence=confidence,
            order_index=order_index,
        )
        self.session.add(claim)
        await self.session.flush()
        return claim

    async def add_evidence_span(
        self,
        claim_id: uuid.UUID,
        paper_id: uuid.UUID,
        evidence_text: str,
        chunk_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
        page_number: int | None = None,
        section: str | None = None,
        relevance_grade: str | None = None,
        retrieval_score: float | None = None,
        reranker_score: float | None = None,
        grader_score: float | None = None,
        source_type: str = "paper",
    ) -> EvidenceSpan:
        span = EvidenceSpan(
            claim_id=claim_id,
            paper_id=paper_id,
            evidence_text=evidence_text,
            chunk_id=chunk_id,
            document_id=document_id,
            page_number=page_number,
            section=section,
            relevance_grade=relevance_grade,
            retrieval_score=retrieval_score,
            reranker_score=reranker_score,
            grader_score=grader_score,
            source_type=source_type,
        )
        self.session.add(span)
        await self.session.flush()
        return span

    async def add_citation(
        self,
        claim_id: uuid.UUID,
        evidence_id: uuid.UUID,
        paper_id: uuid.UUID,
        page_number: int | None = None,
        citation_text: str | None = None,
    ) -> Citation:
        citation = Citation(
            claim_id=claim_id,
            evidence_id=evidence_id,
            paper_id=paper_id,
            page_number=page_number,
            citation_text=citation_text,
        )
        self.session.add(citation)
        await self.session.flush()
        return citation

    async def get_claims_by_message(self, message_id: uuid.UUID) -> list[Claim]:
        stmt = (
            select(Claim)
            .options(
                selectinload(Claim.evidence_spans),
                selectinload(Claim.citations),
            )
            .where(Claim.message_id == message_id)
            .order_by(Claim.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
