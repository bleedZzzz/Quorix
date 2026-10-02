"""Quorix API — Job, job event, saved search, and model request repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.job import Job, JobEvent, ModelRequest


class JobRepository:
    """Repository handling asynchronous jobs, step logs, saved searches, and LLM telemetry."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Jobs
    async def create_job(
        self,
        workspace_id: uuid.UUID,
        job_type: str,
        payload: dict[str, Any],
    ) -> Job:
        job = Job(
            workspace_id=workspace_id,
            job_type=job_type,
            status="queued",
            payload=payload,
            progress=0.0,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_job(
        self,
        job_id: uuid.UUID,
        workspace_id: uuid.UUID | None = None,
    ) -> Job | None:
        stmt = (
            select(Job)
            .options(selectinload(Job.events))
            .where(Job.id == job_id)
        )
        if workspace_id:
            stmt = stmt.where(Job.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_jobs(
        self,
        workspace_id: uuid.UUID,
        status: str | None = None,
        limit: int = 50,
    ) -> list[Job]:
        stmt = select(Job).where(Job.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(Job.status == status)
        stmt = stmt.order_by(Job.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        job_id: uuid.UUID,
        status: str,
        progress: float | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Job | None:
        stmt = select(Job).where(Job.id == job_id)
        res = await self.session.execute(stmt)
        job = res.scalars().first()
        if not job:
            return None

        job.status = status
        if progress is not None:
            job.progress = progress
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        if status == "running" and not job.started_at:
            job.started_at = datetime.now(UTC)
        elif status in ("completed", "failed", "cancelled"):
            job.completed_at = datetime.now(UTC)

        await self.session.flush()
        return job

    async def add_event(
        self,
        job_id: uuid.UUID,
        event_type: str,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> JobEvent:
        event = JobEvent(
            job_id=job_id,
            event_type=event_type,
            message=message,
            data=data or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    # Model Observability Requests
    async def log_model_request(
        self,
        workspace_id: uuid.UUID,
        provider: str,
        model: str,
        task: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        estimated_cost: float | None = None,
        status: str = "success",
        error: str | None = None,
    ) -> ModelRequest:
        req = ModelRequest(
            workspace_id=workspace_id,
            provider=provider,
            model=model,
            task=task,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            estimated_cost=estimated_cost,
            status=status,
            error=error,
        )
        self.session.add(req)
        await self.session.flush()
        return req
