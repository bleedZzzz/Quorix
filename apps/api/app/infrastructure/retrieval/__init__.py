"""Retrieval package."""

from app.infrastructure.retrieval.dense import DenseRetriever
from app.infrastructure.retrieval.hybrid import HybridRetriever
from app.infrastructure.retrieval.interfaces import (
    RetrievalFilters,
    RetrievalResult,
    RetrievalScope,
)
from app.infrastructure.retrieval.lexical import LexicalRetriever

__all__ = [
    "RetrievalScope",
    "RetrievalFilters",
    "RetrievalResult",
    "DenseRetriever",
    "LexicalRetriever",
    "HybridRetriever",
]
