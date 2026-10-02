"""Quorix API — Lexical keyword retriever using PostgreSQL full-text and pattern search."""

from __future__ import annotations

from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.retrieval.interfaces import (
    RetrievalFilters,
    RetrievalResult,
    RetrievalScope,
)


class LexicalRetriever:
    """Retriever performing exact keyword and full-text matching against document chunks."""

    def __init__(self, document_repository: DocumentRepository) -> None:
        self.doc_repo = document_repository

    async def retrieve(
        self,
        query: str,
        scope: RetrievalScope,
        filters: RetrievalFilters | None = None,
        top_k: int = 20,
    ) -> list[RetrievalResult]:
        chunks = await self.doc_repo.search_chunks_lexical(
            workspace_id=scope.workspace_id,
            query_text=query,
            paper_ids=scope.paper_ids,
            top_k=top_k,
        )

        results: list[RetrievalResult] = []
        for rank, chunk in enumerate(chunks):
            # Reciprocal rank heuristic score for lexical matches
            score = 1.0 / (rank + 1)
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    paper_id=chunk.paper_id,
                    document_id=chunk.document_id,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    score=score,
                    retrieval_type="lexical",
                    section_title=chunk.section.title if chunk.section else None,
                    section_type=chunk.section.section_type if chunk.section else None,
                    metadata=chunk.metadata_,
                )
            )
        return results
