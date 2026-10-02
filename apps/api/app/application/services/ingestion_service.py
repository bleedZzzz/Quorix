"""Ingestion pipeline service."""

from __future__ import annotations

import hashlib
import uuid

import httpx

from app.application.ingestion import PDFParser, SectionDetector, SemanticChunker
from app.infrastructure.database.models.document import Document
from app.infrastructure.providers.embeddings import EmbeddingProvider, get_embedding_provider
from app.infrastructure.qdrant.client import QdrantManager
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.paper_repository import PaperRepository
from app.infrastructure.storage.service import StorageService


class IngestionService:
    """Orchestrates end-to-end PDF document ingestion: parsing, section detection, chunking, and embedding."""

    def __init__(
        self,
        paper_repo: PaperRepository,
        doc_repo: DocumentRepository,
        storage_service: StorageService,
        qdrant_manager: QdrantManager,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.paper_repo = paper_repo
        self.doc_repo = doc_repo
        self.storage = storage_service
        self.qdrant = qdrant_manager
        self.embedder = embedding_provider or get_embedding_provider()
        self.parser = PDFParser()
        self.section_detector = SectionDetector()
        self.chunker = SemanticChunker()

    async def ingest_pdf_bytes(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID,
        pdf_bytes: bytes,
        file_name: str = "document.pdf",
    ) -> Document:
        """Execute full parsing, chunking, and vector indexing pipeline for a paper PDF."""
        # 1. Update paper status
        await self.paper_repo.update_status(paper_id, "ingesting")

        checksum = hashlib.sha256(pdf_bytes).hexdigest()
        storage_key = f"workspaces/{workspace_id}/papers/{paper_id}/{checksum}.pdf"

        # 2. Upload to object storage
        await self.storage.upload(key=storage_key, data=pdf_bytes, content_type="application/pdf")

        # 3. Create document record
        document = await self.doc_repo.create(
            paper_id=paper_id,
            storage_key=storage_key,
            file_name=file_name,
            file_size=len(pdf_bytes),
            mime_type="application/pdf",
            checksum=checksum,
        )

        try:
            # 4. Parse PDF layout and text
            parsed = self.parser.parse_bytes(pdf_bytes)
            await self.doc_repo.update_status(document.id, "parsing", page_count=parsed.page_count)

            # 5. Save pages
            pages_data = [
                {
                    "page_number": p.page_number,
                    "text_content": p.text,
                    "width": p.width,
                    "height": p.height,
                }
                for p in parsed.pages
            ]
            await self.doc_repo.save_pages(document.id, pages_data)

            # 6. Detect sections
            detected_sections = self.section_detector.detect_sections(parsed.pages)
            sections_data = [
                {
                    "title": s.title,
                    "section_type": s.section_type,
                    "start_page": s.start_page,
                    "end_page": s.end_page,
                    "level": s.level,
                    "order_index": s.order_index,
                }
                for s in detected_sections
            ]
            saved_sections = await self.doc_repo.save_sections(document.id, sections_data)

            # 7. Semantic chunking
            chunks = self.chunker.chunk_document(parsed.pages, detected_sections)
            chunk_texts = [c.content for c in chunks]

            # 8. Generate embeddings
            embeddings = await self.embedder.embed_documents(chunk_texts)

            # 9. Save chunks to database & prepare vector points
            chunks_to_save = []
            vector_points = []

            for idx, c in enumerate(chunks):
                chunk_id = uuid.uuid4()
                embedding_vec = embeddings[idx] if idx < len(embeddings) else []

                # Find matching section id
                sec_id = None
                for s_obj in saved_sections:
                    if s_obj.title == c.section_title:
                        sec_id = s_obj.id
                        break

                chunks_to_save.append(
                    {
                        "id": chunk_id,
                        "document_id": document.id,
                        "paper_id": paper_id,
                        "workspace_id": workspace_id,
                        "section_id": sec_id,
                        "page_number": c.page_number,
                        "chunk_index": c.chunk_index,
                        "content": c.content,
                        "token_count": c.token_count,
                        "start_offset": c.start_offset,
                        "end_offset": c.end_offset,
                        "embedding_id": str(chunk_id),
                        "text_hash": c.text_hash,
                        "metadata": {
                            "section_title": c.section_title,
                            "section_type": c.section_type,
                        },
                    }
                )

                if embedding_vec:
                    vector_points.append(
                        {
                            "id": str(chunk_id),
                            "vector": embedding_vec,
                            "payload": {
                                "chunk_id": str(chunk_id),
                                "document_id": str(document.id),
                                "paper_id": str(paper_id),
                                "workspace_id": str(workspace_id),
                                "page_number": c.page_number,
                                "content": c.content,
                                "section_title": c.section_title,
                                "section_type": c.section_type,
                            },
                        }
                    )

            await self.doc_repo.save_chunks(chunks_to_save)

            # 10. Index in Qdrant
            if vector_points:
                await self.qdrant.upsert_chunks(vector_points)

            # 11. Finalize status
            await self.doc_repo.update_status(document.id, "parsed")
            await self.paper_repo.update_status(paper_id, "ready")

        except Exception as e:
            await self.doc_repo.update_status(document.id, "failed")
            await self.paper_repo.update_status(paper_id, "failed", metadata_update={"error": str(e)})
            raise

        return document

    async def ingest_from_url(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID,
        pdf_url: str,
    ) -> Document:
        """Download remote PDF and execute ingestion pipeline."""
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(pdf_url)
            resp.raise_for_status()
            pdf_bytes = resp.content

        file_name = pdf_url.split("/")[-1] or "downloaded.pdf"
        if not file_name.endswith(".pdf"):
            file_name += ".pdf"

        return await self.ingest_pdf_bytes(
            workspace_id=workspace_id,
            paper_id=paper_id,
            pdf_bytes=pdf_bytes,
            file_name=file_name,
        )
