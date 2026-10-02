"""Quorix API — Notes, annotations, and tags schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str | None = "#6366f1"


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    color: str | None = None


class NoteCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = ""
    paper_id: uuid.UUID | None = None
    folder: str = "/"


class NoteUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    folder: str | None = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    paper_id: uuid.UUID | None = None
    folder: str | None = "/"
    created_at: datetime
    updated_at: datetime


class AnnotationCreateRequest(BaseModel):
    document_id: uuid.UUID
    page_number: int
    highlight_text: str | None = None
    annotation_text: str | None = None
    color: str | None = "#facc15"
    position_data: dict[str, Any] | None = None


class AnnotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    page_number: int
    highlight_text: str | None = None
    annotation_text: str | None = None
    color: str | None = None
    position_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
