"""Quorix API — LangGraph ResearchState definition."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class ResearchState(TypedDict, total=False):
    # User Input
    query: str
    conversation_id: str | None
    conversation_context: list[dict[str, Any]] | None

    # Analysis & Scope
    intent: str | None  # factual, comparison, summary, gap, review
    rewritten_query: str | None
    query_entities: list[str]
    query_constraints: dict[str, Any]
    workspace_id: str
    project_id: str | None
    paper_ids: list[str] | None

    # Retrieval
    dense_candidates: list[dict[str, Any]]
    lexical_candidates: list[dict[str, Any]]
    merged_candidates: list[dict[str, Any]]
    reranked_evidence: list[dict[str, Any]]

    # Grading & Audit
    graded_evidence: list[dict[str, Any]]
    evidence_sufficient: bool
    knowledge_gaps: list[dict[str, Any]]
    external_sources: list[dict[str, Any]]
    merged_evidence: list[dict[str, Any]]

    # Evidence & Citations
    claims: list[dict[str, Any]]
    citations: list[dict[str, Any]]

    # Output & Diagnostics
    final_answer: str | None
    research_events: list[dict[str, Any]]
    diagnostics: dict[str, Any]
