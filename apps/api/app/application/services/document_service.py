"""Quorix API — Document application service."""

from __future__ import annotations

import uuid

from app.infrastructure.database.models.document import (
    Document,
    DocumentChunk,
    DocumentPage,
    DocumentSection,
)
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.storage.service import StorageService


class DocumentService:
    """Service orchestrating PDF document inspection, pages, sections, and download links."""

    def __init__(
        self,
        doc_repo: DocumentRepository,
        storage_service: StorageService,
    ) -> None:
        self.repo = doc_repo
        self.storage = storage_service

    async def get_document(self, document_id: uuid.UUID) -> Document | None:
        return await self.repo.get_by_id(document_id)

    async def get_download_url(self, storage_key: str, expires_in: int = 3600) -> str:
        return await self.storage.generate_presigned_url(storage_key, expires_in=expires_in)

    async def get_pages(self, document_id: uuid.UUID) -> list[DocumentPage]:
        doc = await self.repo.get_by_id(document_id)
        return doc.pages if doc else []

    async def get_sections(self, document_id: uuid.UUID) -> list[DocumentSection]:
        doc = await self.repo.get_by_id(document_id)
        return doc.sections if doc else []

    async def get_chunks_for_paper(self, paper_id: uuid.UUID) -> list[DocumentChunk]:
        return await self.repo.get_chunks_by_paper(paper_id)
