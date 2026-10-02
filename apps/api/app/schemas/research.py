"""Quorix API — Research graph, gaps, reviews, and screening schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RelationshipCreateRequest(BaseModel):
    source_paper_id: uuid.UUID
    target_paper_id: uuid.UUID
    relationship_type: str  # cites, cited_by, builds_on, extends, contradicts, supports, similar_to
    confidence: float | None = None
    evidence_ids: list[uuid.UUID] = Field(default_factory=list)


class RelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    source_paper_id: uuid.UUID
    target_paper_id: uuid.UUID
    relationship_type: str
    confidence: float | None = None
    evidence_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: datetime


class GapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    gap_description: str
    gap_type: str | None = None
    confidence: float | None = None
    why_detected: str | None = None
    potential_direction: str | None = None
    supporting_paper_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: datetime


class ReviewCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    research_question: str | None = None
    scope: str | None = None
    inclusion_criteria: str | None = None
    exclusion_criteria: str | None = None


class ScreeningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    review_id: uuid.UUID
    paper_id: uuid.UUID
    status: str
    reason: str | None = None
    screened_at: datetime | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    research_question: str | None = None
    scope: str | None = None
    inclusion_criteria: str | None = None
    exclusion_criteria: str | None = None
    notes: str | None = None
    synthesis: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    screenings: list[ScreeningResponse] = Field(default_factory=list)
