"""Quorix API — Embedding provider interface and implementations."""

from __future__ import annotations

import hashlib
import math
from abc import ABC, abstractmethod

import httpx

from app.config.settings import settings


class EmbeddingProvider(ABC):
    """Abstract interface for generating dense vector embeddings."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for a search query."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of document chunks."""
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hash-based embedding provider for testing and development."""

    def __init__(self, dim: int = 1536) -> None:
        self.dim = dim

    def _hash_to_vector(self, text: str) -> list[float]:
        # Generate pseudo-random vector deterministically seeded by text hash
        vec = []
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        for i in range(self.dim):
            val = math.sin(seed + i * 0.1)
            vec.append(val)
        # Normalize to unit vector
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    async def embed_query(self, text: str) -> list[float]:
        return self._hash_to_vector(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_to_vector(t) for t in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings API (text-embedding-3-small)."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def embed_query(self, text: str) -> list[float]:
        res = await self.embed_documents([text])
        return res[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "input": texts,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.openai_api_key:
        return OpenAIEmbeddingProvider(api_key=settings.openai_api_key)
    return MockEmbeddingProvider()
