"""Document schemas."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    page_number: int
    text_content: str | None = None
    width: float | None = None
    height: float | None = None


class DocumentSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None = None
    section_type: str | None = None
    start_page: int | None = None
    end_page: int | None = None
    level: int
    order_index: int


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    chunk_index: int
    content: str
    token_count: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    section_title: str | None = None
    section_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paper_id: uuid.UUID
    storage_key: str
    file_name: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    checksum: str | None = None
    page_count: int | None = None
    status: str
    created_at: str
    download_url: str | None = None
