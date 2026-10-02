"""Quorix API — Documents endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.document_service import DocumentService
from app.dependencies import get_document_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentPageResponse,
    DocumentResponse,
    DocumentSectionResponse,
)
from app.security.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ApiResponse[DocumentResponse]:
    """Get document details."""
    doc = await service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    download_url = await service.get_download_url(doc.storage_key)
    res = DocumentResponse(
        id=doc.id,
        paper_id=doc.paper_id,
        storage_key=doc.storage_key,
        file_name=doc.file_name,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        checksum=doc.checksum,
        page_count=doc.page_count,
        status=doc.status,
        created_at=str(doc.created_at),
        download_url=download_url,
    )
    return ApiResponse(data=res)


@router.get("/{document_id}/pages", response_model=ApiResponse[list[DocumentPageResponse]])
async def get_document_pages(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ApiResponse[list[DocumentPageResponse]]:
    """Get parsed pages for document."""
    pages = await service.get_pages(document_id)
    return ApiResponse(data=[DocumentPageResponse.model_validate(p) for p in pages])


@router.get("/{document_id}/sections", response_model=ApiResponse[list[DocumentSectionResponse]])
async def get_document_sections(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ApiResponse[list[DocumentSectionResponse]]:
    """Get detected section hierarchy for document."""
    sections = await service.get_sections(document_id)
    return ApiResponse(data=[DocumentSectionResponse.model_validate(s) for s in sections])


@router.get("/paper/{paper_id}/chunks", response_model=ApiResponse[list[DocumentChunkResponse]])
async def get_paper_chunks(
    paper_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> ApiResponse[list[DocumentChunkResponse]]:
    """Get all semantic chunks for a paper."""
    chunks = await service.get_chunks_for_paper(paper_id)
    chunk_responses = []
    for c in chunks:
        chunk_responses.append(
            DocumentChunkResponse(
                id=c.id,
                paper_id=c.paper_id,
                document_id=c.document_id,
                page_number=c.page_number,
                chunk_index=c.chunk_index,
                content=c.content,
                token_count=c.token_count,
                start_offset=c.start_offset,
                end_offset=c.end_offset,
                section_title=c.section.title if c.section else None,
                section_type=c.section.section_type if c.section else None,
                metadata=c.metadata_,
            )
        )
    return ApiResponse(data=chunk_responses)
