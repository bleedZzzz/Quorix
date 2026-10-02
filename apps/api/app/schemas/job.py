"""Job and Discovery schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    event_type: str
    message: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    job_type: str
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None
    progress: float
    retry_count: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    events: list[JobEventResponse] = Field(default_factory=list)


class DiscoverySearchResult(BaseModel):
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    authors: list[str] = Field(default_factory=list)
    pdf_url: str | None = None
    source: str  # arxiv, openalex, semantic_scholar
    citation_count: int | None = None


class DiscoverySearchResponse(BaseModel):
    results: list[DiscoverySearchResult]
    query: str
    total: int
