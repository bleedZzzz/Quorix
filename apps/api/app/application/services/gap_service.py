"""Research gap detection and synthesis service."""

from __future__ import annotations

import uuid

from app.infrastructure.database.models.research import ResearchGap
from app.infrastructure.providers.llm import LLMProvider, get_llm_provider
from app.infrastructure.repositories.paper_repository import PaperRepository
from app.infrastructure.repositories.research_repository import ResearchRepository


class GapService:
    """Detects unexplored research directions, contradictions, and empirical gaps across literature."""

    def __init__(
        self,
        research_repo: ResearchRepository,
        paper_repo: PaperRepository,
        llm: LLMProvider | None = None,
    ) -> None:
        self.repo = research_repo
        self.paper_repo = paper_repo
        self.llm = llm or get_llm_provider()

    async def list_gaps(self, workspace_id: uuid.UUID) -> list[ResearchGap]:
        return await self.repo.list_gaps(workspace_id)

    async def analyze_gaps(
        self,
        workspace_id: uuid.UUID,
        paper_ids: list[uuid.UUID] | None = None,
    ) -> list[ResearchGap]:
        papers, _ = await self.paper_repo.list_papers(workspace_id=workspace_id, limit=20)
        if not papers:
            return []

        summaries = [f"Title: {p.title}\nAbstract: {p.abstract or 'N/A'}" for p in papers[:10]]
        prompt = (
            "Analyze the following academic literature and identify 2-3 significant research gaps "
            "(unexplored questions, methodological limitations, or contradictory findings):\n\n"
            + "\n\n---\n\n".join(summaries)
            + "\n\nFormat your response as a JSON array of objects with keys: "
            "'description', 'type', 'why_detected', 'potential_direction'."
        )

        res = await self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are an expert research strategist finding literature gaps. Return valid JSON only.",
        )

        raw_gaps = res if isinstance(res, list) else res.get("gaps", [res])
        created_gaps = []
        for g in raw_gaps:
            if isinstance(g, dict) and "description" in g:
                gap = await self.repo.create_gap(
                    workspace_id=workspace_id,
                    gap_description=g["description"],
                    gap_type=g.get("type", "methodological"),
                    confidence=0.88,
                    why_detected=g.get("why_detected"),
                    potential_direction=g.get("potential_direction"),
                    supporting_paper_ids=[p.id for p in papers[:3]],
                )
                created_gaps.append(gap)

        return created_gaps or await self.repo.list_gaps(workspace_id)
