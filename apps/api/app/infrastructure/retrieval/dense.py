"""Dense semantic retriever using Qdrant."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.infrastructure.providers.embeddings import EmbeddingProvider, get_embedding_provider
from app.infrastructure.qdrant.client import QdrantManager
from app.infrastructure.retrieval.interfaces import (
    RetrievalFilters,
    RetrievalResult,
    RetrievalScope,
)

if TYPE_CHECKING:
    from app.infrastructure.repositories.document_repository import DocumentRepository


class DenseRetriever:
    """Retriever performing semantic vector search against Qdrant collection."""

    def __init__(
        self,
        qdrant: QdrantManager,
        embedding_provider: EmbeddingProvider | None = None,
        doc_repo: DocumentRepository | None = None,
    ) -> None:
        self.qdrant = qdrant
        self.embedder = embedding_provider or get_embedding_provider()
        self.doc_repo = doc_repo

    async def retrieve(
        self,
        query: str,
        scope: RetrievalScope,
        filters: RetrievalFilters | None = None,
        top_k: int = 20,
    ) -> list[RetrievalResult]:
        query_vec = await self.embedder.embed_query(query)
        hits = await self.qdrant.search(
            vector=query_vec,
            workspace_id=scope.workspace_id,
            paper_ids=scope.paper_ids,
            top_k=top_k,
        )

        results: list[RetrievalResult] = []
        for hit in hits:
            payload = hit.get("payload") or {}
            chunk_id_str = payload.get("chunk_id") or hit["id"]
            results.append(
                RetrievalResult(
                    chunk_id=uuid.UUID(str(chunk_id_str)),
                    paper_id=uuid.UUID(str(payload.get("paper_id"))),
                    document_id=uuid.UUID(str(payload.get("document_id"))),
                    page_number=int(payload.get("page_number", 1)),
                    content=payload.get("content", ""),
                    score=float(hit["score"]),
                    retrieval_type="dense",
                    section_title=payload.get("section_title"),
                    section_type=payload.get("section_type"),
                    metadata=payload.get("metadata", {}),
                )
            )
        return results
