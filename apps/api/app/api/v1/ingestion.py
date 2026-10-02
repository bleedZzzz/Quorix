"""Quorix API — Ingestion endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.application.services.ingestion_service import IngestionService
from app.dependencies import get_ingestion_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.document import DocumentResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class IngestUrlRequest(BaseModel):
    workspace_id: uuid.UUID
    paper_id: uuid.UUID
    pdf_url: str


@router.post("/upload", response_model=ApiResponse[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    workspace_id: uuid.UUID = Form(...),
    paper_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: IngestionService = Depends(get_ingestion_service),
) -> ApiResponse[DocumentResponse]:
    """Upload a PDF file and trigger parsing, chunking, and vector indexing."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    document = await service.ingest_pdf_bytes(
        workspace_id=workspace_id,
        paper_id=paper_id,
        pdf_bytes=content,
        file_name=file.filename or "uploaded.pdf",
    )

    download_url = await service.storage.generate_presigned_url(document.storage_key)
    res = DocumentResponse(
        id=document.id,
        paper_id=document.paper_id,
        storage_key=document.storage_key,
        file_name=document.file_name,
        file_size=document.file_size,
        mime_type=document.mime_type,
        checksum=document.checksum,
        page_count=document.page_count,
        status=document.status,
        created_at=str(document.created_at),
        download_url=download_url,
    )
    return ApiResponse(data=res)


@router.post("/url", response_model=ApiResponse[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def ingest_url(
    request: IngestUrlRequest,
    current_user: User = Depends(get_current_user),
    service: IngestionService = Depends(get_ingestion_service),
) -> ApiResponse[DocumentResponse]:
    """Download a remote PDF and execute ingestion pipeline."""
    document = await service.ingest_from_url(
        workspace_id=request.workspace_id,
        paper_id=request.paper_id,
        pdf_url=request.pdf_url,
    )

    download_url = await service.storage.generate_presigned_url(document.storage_key)
    res = DocumentResponse(
        id=document.id,
        paper_id=document.paper_id,
        storage_key=document.storage_key,
        file_name=document.file_name,
        file_size=document.file_size,
        mime_type=document.mime_type,
        checksum=document.checksum,
        page_count=document.page_count,
        status=document.status,
        created_at=str(document.created_at),
        download_url=download_url,
    )
    return ApiResponse(data=res)
