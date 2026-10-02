"""Paper schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuthorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    affiliation: str | None = None
    external_ids: dict[str, Any] = Field(default_factory=dict)


class PaperAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    author: AuthorSchema


class PaperSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    external_id: str
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class PaperCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    pdf_url: str | None = None
    paper_type: str = "article"
    authors: list[AuthorSchema] = Field(default_factory=list)
    sources: list[PaperSourceSchema] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaperUpdateRequest(BaseModel):
    title: str | None = None
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    status: str | None = None
    metadata: dict[str, Any] | None = None


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    abstract: str | None = None
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    pdf_url: str | None = None
    status: str
    paper_type: str | None = None
    authors: list[PaperAuthorResponse] = Field(default_factory=list)
    sources: list[PaperSourceSchema] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime


class PaperListResponse(BaseModel):
    items: list[PaperResponse]
    total: int
    limit: int
    offset: int
