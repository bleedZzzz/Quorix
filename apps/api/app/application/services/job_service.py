"""Quorix API — Background jobs and event service."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.database.models.job import Job
from app.infrastructure.repositories.job_repository import JobRepository


class JobService:
    """Orchestrates background tasks, job states, and progress telemetry."""

    def __init__(self, job_repo: JobRepository) -> None:
        self.repo = job_repo

    async def enqueue_job(
        self,
        workspace_id: uuid.UUID,
        job_type: str,
        payload: dict[str, Any],
    ) -> Job:
        job = await self.repo.create_job(workspace_id=workspace_id, job_type=job_type, payload=payload)
        await self.repo.add_event(job.id, "queued", "Job added to processing queue")
        return job

    async def get_job(self, job_id: uuid.UUID, workspace_id: uuid.UUID | None = None) -> Job | None:
        return await self.repo.get_job(job_id, workspace_id)

    async def list_jobs(
        self,
        workspace_id: uuid.UUID,
        status: str | None = None,
        limit: int = 50,
    ) -> list[Job]:
        return await self.repo.list_jobs(workspace_id=workspace_id, status=status, limit=limit)

    async def update_progress(
        self,
        job_id: uuid.UUID,
        progress: float,
        message: str | None = None,
    ) -> Job | None:
        job = await self.repo.update_status(job_id=job_id, status="running", progress=progress)
        if message:
            await self.repo.add_event(job_id, "progress", message, {"progress": progress})
        return job

    async def complete_job(
        self,
        job_id: uuid.UUID,
        result: dict[str, Any],
        message: str = "Job completed successfully",
    ) -> Job | None:
        job = await self.repo.update_status(job_id=job_id, status="completed", progress=1.0, result=result)
        await self.repo.add_event(job_id, "completed", message, result)
        return job

    async def fail_job(
        self,
        job_id: uuid.UUID,
        error: str,
    ) -> Job | None:
        job = await self.repo.update_status(job_id=job_id, status="failed", error=error)
        await self.repo.add_event(job_id, "failed", f"Job failed: {error}", {"error": error})
        return job
