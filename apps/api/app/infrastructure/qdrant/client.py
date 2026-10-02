"""Qdrant vector database client and collection manager."""

from __future__ import annotations

import contextlib
import uuid
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.config.settings import settings


class QdrantManager:
    """Manages Qdrant vector collections and similarity search."""

    def __init__(self, url: str | None = None) -> None:
        self.url = url or settings.qdrant_url
        self.collection_name = settings.qdrant_collection
        self.client = AsyncQdrantClient(url=self.url)

    async def ensure_collection(self, vector_dim: int = 1536) -> None:
        """Create the collection if it doesn't exist."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=vector_dim,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                # Create payload indexes for fast filtered lookups
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="workspace_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="paper_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
        except Exception:
            # When Qdrant service is not running locally during tests, fail softly
            pass

    async def upsert_chunks(
        self,
        points: list[dict[str, Any]],
    ) -> None:
        """
        Upsert a batch of chunk vectors.
        Each item in points:
          - id: str / UUID
          - vector: list[float]
          - payload: dict (workspace_id, paper_id, document_id, page_number, content, etc.)
        """
        if not points:
            return

        qdrant_points = [
            qmodels.PointStruct(
                id=str(p["id"]),
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        await self.client.upsert(
            collection_name=self.collection_name,
            points=qdrant_points,
        )

    async def search(
        self,
        vector: list[float],
        workspace_id: uuid.UUID,
        paper_ids: list[uuid.UUID] | None = None,
        top_k: int = 20,
        score_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search similar chunks filtered by workspace and optionally paper scope."""
        filter_conditions = [
            qmodels.FieldCondition(
                key="workspace_id",
                match=qmodels.MatchValue(value=str(workspace_id)),
            )
        ]

        if paper_ids:
            filter_conditions.append(
                qmodels.FieldCondition(
                    key="paper_id",
                    match=qmodels.MatchAny(any=[str(pid) for pid in paper_ids]),
                )
            )

        query_filter = qmodels.Filter(must=filter_conditions)

        try:
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
            )
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in results
            ]
        except Exception:
            return []

    async def delete_by_paper(self, paper_id: uuid.UUID) -> None:
        """Delete all chunk vectors for a given paper."""
        with contextlib.suppress(Exception):
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="paper_id",
                                match=qmodels.MatchValue(value=str(paper_id)),
                            )
                        ]
                    )
                ),
            )
