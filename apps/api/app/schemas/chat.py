"""Quorix API — Chat, conversation, claim, and citation schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    evidence_id: uuid.UUID
    paper_id: uuid.UUID
    page_number: int | None = None
    citation_text: str | None = None


class EvidenceSpanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_id: uuid.UUID
    chunk_id: uuid.UUID | None = None
    paper_id: uuid.UUID
    page_number: int | None = None
    section: str | None = None
    evidence_text: str
    relevance_grade: str | None = None
    retrieval_score: float | None = None
    reranker_score: float | None = None
    grader_score: float | None = None
    source_type: str


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_text: str
    verification_state: str
    confidence: float | None = None
    order_index: int
    evidence_spans: list[EvidenceSpanResponse] = Field(default_factory=list)
    citations: list[CitationResponse] = Field(default_factory=list)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    claims: list[ClaimResponse] = Field(default_factory=list)


class ConversationCreateRequest(BaseModel):
    title: str = "New Research Session"
    scope_type: str = "workspace"
    scope_ids: list[uuid.UUID] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    scope_type: str
    scope_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)


class ChatMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    paper_ids: list[uuid.UUID] | None = None
