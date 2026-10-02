"""Retrieval interfaces and data models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalScope:
    workspace_id: uuid.UUID
    paper_ids: list[uuid.UUID] | None = None
    project_id: uuid.UUID | None = None


@dataclass
class RetrievalFilters:
    year_min: int | None = None
    year_max: int | None = None
    section_types: list[str] | None = None
    sources: list[str] | None = None


@dataclass
class RetrievalResult:
    chunk_id: uuid.UUID
    paper_id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    content: str
    score: float
    retrieval_type: str  # "dense", "lexical", "hybrid"
    section_title: str | None = None
    section_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
