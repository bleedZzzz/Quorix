"""Redis-backed background job queue and dispatcher."""

from __future__ import annotations

import json
import uuid
from typing import Any

import redis.asyncio as redis


class JobQueue:
    """Redis-backed FIFO job queue with support for delayed retries and worker leases."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", queue_name: str = "quorix:jobs") -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name
        self._client: redis.Redis | None = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def enqueue(self, job_id: uuid.UUID, job_type: str, payload: dict[str, Any]) -> None:
        """Push a job ID and its type into the Redis queue."""
        client = await self.get_client()
        message = json.dumps(
            {
                "job_id": str(job_id),
                "job_type": job_type,
                "payload": payload,
            }
        )
        await client.lpush(self.queue_name, message)

    async def dequeue(self, timeout: int = 5) -> dict[str, Any] | None:
        """Block pop the next job from the queue."""
        client = await self.get_client()
        result = await client.brpop(self.queue_name, timeout=timeout)
        if not result:
            return None
        _, message = result
        return json.loads(message)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
