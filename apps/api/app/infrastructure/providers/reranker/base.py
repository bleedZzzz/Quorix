"""Reranker provider interface and implementations."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod


class RerankerProvider(ABC):
    """Abstract interface for cross-encoder or semantic reranking."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 10,
    ) -> list[tuple[int, float]]:
        """
        Rerank a list of documents against a query.
        Returns a list of (original_index, relevance_score) sorted descending by score.
        """
        pass


class HeuristicRerankerProvider(RerankerProvider):
    """
    Term overlap and proximity heuristic reranker for zero-dependency / fallback environments.
    Scores candidates based on query term frequency, phrase matches, and document length normalization.
    """

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 10,
    ) -> list[tuple[int, float]]:
        if not documents:
            return []

        query_terms = set(re.findall(r"\w+", query.lower()))
        scored = []

        for idx, doc in enumerate(documents):
            doc_lower = doc.lower()
            doc_words = re.findall(r"\w+", doc_lower)
            doc_len = len(doc_words) or 1

            # Exact phrase bonus
            exact_phrase_bonus = 2.0 if query.lower() in doc_lower else 0.0

            # Term frequency
            matches = sum(1 for w in doc_words if w in query_terms)
            unique_matches = sum(1 for t in query_terms if t in doc_lower)

            # Score formula
            coverage = unique_matches / (len(query_terms) or 1)
            density = matches / doc_len
            score = (coverage * 0.6) + (density * 0.2) + (exact_phrase_bonus * 0.2)

            scored.append((idx, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]


def get_reranker_provider() -> RerankerProvider:
    return HeuristicRerankerProvider()
