"""Papers endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.paper_service import PaperService
from app.dependencies import get_paper_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.paper import (
    PaperCreateRequest,
    PaperListResponse,
    PaperResponse,
    PaperUpdateRequest,
)
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("", response_model=ApiResponse[PaperResponse], status_code=status.HTTP_201_CREATED)
async def create_paper(
    workspace_id: uuid.UUID = Query(...),
    request: PaperCreateRequest = ...,
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: PaperService = Depends(get_paper_service),
) -> ApiResponse[PaperResponse]:
    """Import or register a paper in the workspace."""
    paper = await service.create_paper(workspace_id, request)
    return ApiResponse(data=PaperResponse.model_validate(paper))


@router.get("", response_model=ApiResponse[PaperListResponse])
async def list_papers(
    workspace_id: uuid.UUID = Query(...),
    status: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: PaperService = Depends(get_paper_service),
) -> ApiResponse[PaperListResponse]:
    """List papers within a workspace with search and pagination."""
    papers, total = await service.list_papers(
        workspace_id=workspace_id,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=PaperListResponse(
            items=[PaperResponse.model_validate(p) for p in papers],
            total=total,
            limit=limit,
            offset=offset,
        )
    )


@router.get("/{paper_id}", response_model=ApiResponse[PaperResponse])
async def get_paper(
    paper_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: PaperService = Depends(get_paper_service),
) -> ApiResponse[PaperResponse]:
    """Get paper details by ID."""
    paper = await service.get_paper(paper_id, workspace_id)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return ApiResponse(data=PaperResponse.model_validate(paper))


@router.put("/{paper_id}", response_model=ApiResponse[PaperResponse])
async def update_paper(
    paper_id: uuid.UUID,
    request: PaperUpdateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: PaperService = Depends(get_paper_service),
) -> ApiResponse[PaperResponse]:
    """Update paper metadata or processing status."""
    paper = await service.update_paper(paper_id, workspace_id, request)
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return ApiResponse(data=PaperResponse.model_validate(paper))


@router.delete("/{paper_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_paper(
    paper_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: PaperService = Depends(get_paper_service),
) -> ApiResponse[dict[str, bool]]:
    """Delete a paper from the workspace."""
    deleted = await service.delete_paper(paper_id, workspace_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return ApiResponse(data={"deleted": True})
