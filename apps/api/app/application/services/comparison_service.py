"""Quorix API — Literature comparison matrix service."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.providers.llm import LLMProvider, get_llm_provider
from app.infrastructure.repositories.paper_repository import PaperRepository


class ComparisonService:
    """Generates structured cross-paper comparative analyses."""

    def __init__(self, paper_repo: PaperRepository, llm: LLMProvider | None = None) -> None:
        self.paper_repo = paper_repo
        self.llm = llm or get_llm_provider()

    async def compare_papers(
        self,
        workspace_id: uuid.UUID,
        paper_ids: list[uuid.UUID],
        dimensions: list[str] | None = None,
    ) -> dict[str, Any]:
        target_dimensions = dimensions or ["Methodology", "Datasets", "Primary Findings", "Limitations"]
        papers = []
        for pid in paper_ids:
            p = await self.paper_repo.get_by_id(pid, workspace_id)
            if p:
                papers.append(p)

        if not papers:
            return {"error": "No valid papers found for comparison", "matrix": {}}

        paper_summaries = []
        for p in papers:
            paper_summaries.append(
                f"Paper: {p.title} ({p.year or 'N/A'})\nAbstract: {p.abstract or 'No abstract provided'}"
            )

        prompt = (
            f"Compare the following papers across these dimensions: {', '.join(target_dimensions)}.\n\n"
            + "\n\n---\n\n".join(paper_summaries)
            + "\n\nFormat your output as structured JSON where keys are the paper titles and values are objects mapping each dimension to a concise assessment."
        )

        matrix = await self.llm.generate_json(
            prompt=prompt,
            system_prompt="You are an expert scientific reviewer compiling a comparative synthesis table. Return valid JSON only.",
        )

        return {
            "workspace_id": str(workspace_id),
            "paper_count": len(papers),
            "dimensions": target_dimensions,
            "matrix": matrix,
        }
