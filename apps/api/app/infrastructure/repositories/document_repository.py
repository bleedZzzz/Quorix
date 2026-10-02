"""Document repository for PDF files, pages, sections, and chunks."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.document import (
    Document,
    DocumentChunk,
    DocumentPage,
    DocumentSection,
)


class DocumentRepository:
    """Repository handling CRUD and queries for documents, pages, sections, and chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        paper_id: uuid.UUID,
        storage_key: str,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str = "application/pdf",
        checksum: str | None = None,
    ) -> Document:
        doc = Document(
            paper_id=paper_id,
            storage_key=storage_key,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            checksum=checksum,
            status="uploaded",
        )
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        stmt = (
            select(Document)
            .options(
                selectinload(Document.pages),
                selectinload(Document.sections),
            )
            .where(Document.id == document_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_paper_id(self, paper_id: uuid.UUID) -> list[Document]:
        stmt = select(Document).where(Document.paper_id == paper_id).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: uuid.UUID,
        status: str,
        page_count: int | None = None,
    ) -> Document | None:
        doc = await self.get_by_id(document_id)
        if not doc:
            return None
        doc.status = status
        if page_count is not None:
            doc.page_count = page_count
        await self.session.flush()
        return doc

    async def save_pages(
        self,
        document_id: uuid.UUID,
        pages_data: list[dict[str, Any]],
    ) -> list[DocumentPage]:
        pages = []
        for p in pages_data:
            page = DocumentPage(
                document_id=document_id,
                page_number=p["page_number"],
                text_content=p.get("text_content"),
                width=p.get("width"),
                height=p.get("height"),
            )
            self.session.add(page)
            pages.append(page)
        await self.session.flush()
        return pages

    async def save_sections(
        self,
        document_id: uuid.UUID,
        sections_data: list[dict[str, Any]],
    ) -> list[DocumentSection]:
        sections = []
        for s in sections_data:
            section = DocumentSection(
                document_id=document_id,
                title=s.get("title"),
                section_type=s.get("section_type"),
                start_page=s.get("start_page"),
                end_page=s.get("end_page"),
                level=s.get("level", 1),
                order_index=s.get("order_index", 0),
            )
            self.session.add(section)
            sections.append(section)
        await self.session.flush()
        return sections

    async def save_chunks(
        self,
        chunks_data: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        chunks = []
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=c["document_id"],
                paper_id=c["paper_id"],
                workspace_id=c["workspace_id"],
                section_id=c.get("section_id"),
                page_number=c["page_number"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                token_count=c.get("token_count"),
                start_offset=c.get("start_offset"),
                end_offset=c.get("end_offset"),
                embedding_id=c.get("embedding_id"),
                text_hash=c.get("text_hash"),
                metadata_=c.get("metadata", {}),
            )
            self.session.add(chunk)
            chunks.append(chunk)
        await self.session.flush()
        return chunks

    async def get_chunks_by_paper(
        self,
        paper_id: uuid.UUID,
        limit: int | None = None,
    ) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.paper_id == paper_id)
            .order_by(DocumentChunk.page_number, DocumentChunk.chunk_index)
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_chunks_by_ids(self, chunk_ids: list[uuid.UUID]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []
        stmt = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.section))
            .where(DocumentChunk.id.in_(chunk_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_chunks_lexical(
        self,
        workspace_id: uuid.UUID,
        query_text: str,
        paper_ids: list[uuid.UUID] | None = None,
        top_k: int = 20,
    ) -> list[DocumentChunk]:
        """Lexical candidate search using pattern matching and full text scoring."""
        stmt = select(DocumentChunk).where(
            DocumentChunk.workspace_id == workspace_id,
            DocumentChunk.content.ilike(f"%{query_text}%"),
        )
        if paper_ids:
            stmt = stmt.where(DocumentChunk.paper_id.in_(paper_ids))
        stmt = stmt.limit(top_k)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
