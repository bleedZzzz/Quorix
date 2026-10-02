"""Hybrid retriever combining Dense & Lexical search with Reciprocal Rank Fusion (RRF)."""

from __future__ import annotations

import asyncio
import uuid

from app.infrastructure.providers.reranker import RerankerProvider, get_reranker_provider
from app.infrastructure.retrieval.dense import DenseRetriever
from app.infrastructure.retrieval.interfaces import (
    RetrievalFilters,
    RetrievalResult,
    RetrievalScope,
)
from app.infrastructure.retrieval.lexical import LexicalRetriever


class HybridRetriever:
    """Combines dense semantic vector search with lexical search using Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        lexical_retriever: LexicalRetriever,
        reranker: RerankerProvider | None = None,
        rrf_k: int = 60,
    ) -> None:
        self.dense = dense_retriever
        self.lexical = lexical_retriever
        self.reranker = reranker or get_reranker_provider()
        self.rrf_k = rrf_k

    async def retrieve(
        self,
        query: str,
        scope: RetrievalScope,
        filters: RetrievalFilters | None = None,
        top_k: int = 20,
        rerank: bool = True,
    ) -> list[RetrievalResult]:
        # Run dense and lexical retrieval concurrently
        dense_candidates, lexical_candidates = await asyncio.gather(
            self.dense.retrieve(query, scope, filters, top_k=top_k * 2),
            self.lexical.retrieve(query, scope, filters, top_k=top_k * 2),
        )

        # Merge using Reciprocal Rank Fusion (RRF)
        # RRF score = sum(1 / (k + rank_i))
        scores: dict[uuid.UUID, float] = {}
        candidate_map: dict[uuid.UUID, RetrievalResult] = {}

        for rank, item in enumerate(dense_candidates):
            scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            candidate_map[item.chunk_id] = item

        for rank, item in enumerate(lexical_candidates):
            scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if item.chunk_id not in candidate_map:
                candidate_map[item.chunk_id] = item

        merged = [
            RetrievalResult(
                chunk_id=cid,
                paper_id=candidate_map[cid].paper_id,
                document_id=candidate_map[cid].document_id,
                page_number=candidate_map[cid].page_number,
                content=candidate_map[cid].content,
                score=scores[cid],
                retrieval_type="hybrid",
                section_title=candidate_map[cid].section_title,
                section_type=candidate_map[cid].section_type,
                metadata=candidate_map[cid].metadata,
            )
            for cid in scores
        ]
        merged.sort(key=lambda x: x.score, reverse=True)
        top_candidates = merged[: top_k * 2]

        if not rerank or not top_candidates:
            return top_candidates[:top_k]

        # Rerank with cross-encoder / heuristic reranker
        documents = [c.content for c in top_candidates]
        reranked_indices = await self.reranker.rerank(query, documents, top_n=top_k)

        final_results = []
        for orig_idx, rerank_score in reranked_indices:
            candidate = top_candidates[orig_idx]
            candidate.score = rerank_score
            final_results.append(candidate)

        return final_results
