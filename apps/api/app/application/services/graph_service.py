"""Quorix API — Knowledge graph and relationship service."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.database.models.research import PaperRelationship
from app.infrastructure.repositories.paper_repository import PaperRepository
from app.infrastructure.repositories.research_repository import ResearchRepository


class GraphService:
    """Orchestrates research citation graph extraction and traversal."""

    def __init__(self, research_repo: ResearchRepository, paper_repo: PaperRepository) -> None:
        self.repo = research_repo
        self.paper_repo = paper_repo

    async def create_relationship(
        self,
        workspace_id: uuid.UUID,
        source_paper_id: uuid.UUID,
        target_paper_id: uuid.UUID,
        relationship_type: str,
        confidence: float | None = None,
        evidence_ids: list[uuid.UUID] | None = None,
    ) -> PaperRelationship:
        return await self.repo.create_relationship(
            workspace_id=workspace_id,
            source_paper_id=source_paper_id,
            target_paper_id=target_paper_id,
            relationship_type=relationship_type,
            confidence=confidence,
            evidence_ids=evidence_ids,
        )

    async def get_graph(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        relationships = await self.repo.get_relationships(workspace_id=workspace_id, paper_id=paper_id)
        papers, _ = await self.paper_repo.list_papers(workspace_id=workspace_id, limit=200)

        nodes = [
            {
                "id": str(p.id),
                "label": p.title[:60] + "..." if len(p.title) > 60 else p.title,
                "title": p.title,
                "year": p.year,
                "venue": p.venue,
                "status": p.status,
            }
            for p in papers
        ]

        edges = [
            {
                "id": str(r.id),
                "source": str(r.source_paper_id),
                "target": str(r.target_paper_id),
                "type": r.relationship_type,
                "confidence": r.confidence,
            }
            for r in relationships
        ]

        return {"nodes": nodes, "edges": edges}
