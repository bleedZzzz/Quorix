"""Quorix API — Background jobs endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.application.services.job_service import JobService
from app.dependencies import get_job_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job import JobResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/jobs", tags=["jobs"])


class CreateJobRequest(BaseModel):
    job_type: str
    payload: dict[str, Any]


@router.post("", response_model=ApiResponse[JobResponse], status_code=status.HTTP_201_CREATED)
async def create_job(
    request: CreateJobRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: JobService = Depends(get_job_service),
) -> ApiResponse[JobResponse]:
    """Enqueue a new background processing job."""
    job = await service.enqueue_job(
        workspace_id=workspace_id,
        job_type=request.job_type,
        payload=request.payload,
    )
    return ApiResponse(data=JobResponse.model_validate(job))


@router.get("", response_model=ApiResponse[list[JobResponse]])
async def list_jobs(
    workspace_id: uuid.UUID = Query(...),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: JobService = Depends(get_job_service),
) -> ApiResponse[list[JobResponse]]:
    """List background jobs in workspace."""
    jobs = await service.list_jobs(workspace_id=workspace_id, status=status, limit=limit)
    return ApiResponse(data=[JobResponse.model_validate(j) for j in jobs])


@router.get("/{job_id}", response_model=ApiResponse[JobResponse])
async def get_job(
    job_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: JobService = Depends(get_job_service),
) -> ApiResponse[JobResponse]:
    """Get background job details and event history."""
    job = await service.get_job(job_id, workspace_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return ApiResponse(data=JobResponse.model_validate(job))
