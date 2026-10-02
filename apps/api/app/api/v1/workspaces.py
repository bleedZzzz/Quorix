"""Quorix API — Workspace endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.workspace_service import WorkspaceError, WorkspaceService
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceResponse,
)
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=ApiResponse[list[WorkspaceResponse]])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(),
) -> ApiResponse:
    """List all workspaces for the current user."""
    service = WorkspaceService(session)
    workspaces = await service.list_user_workspaces(current_user.id)
    return ApiResponse(
        data=[WorkspaceResponse.model_validate(w) for w in workspaces]
    )


@router.post(
    "",
    response_model=ApiResponse[WorkspaceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    request: CreateWorkspaceRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(),
) -> ApiResponse:
    """Create a new workspace."""
    service = WorkspaceService(session)
    try:
        workspace = await service.create_workspace(request, current_user.id)
    except WorkspaceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return ApiResponse(data=WorkspaceResponse.model_validate(workspace))


@router.get("/{workspace_id}", response_model=ApiResponse[WorkspaceResponse])
async def get_workspace(
    workspace_id: UUID,
    _member=Depends(get_workspace_member),
    session: AsyncSession = Depends(),
) -> ApiResponse:
    """Get workspace details. Requires membership."""
    service = WorkspaceService(session)
    try:
        workspace = await service.get_workspace(workspace_id)
    except WorkspaceError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return ApiResponse(data=WorkspaceResponse.model_validate(workspace))


@router.put("/{workspace_id}", response_model=ApiResponse[WorkspaceResponse])
async def update_workspace(
    workspace_id: UUID,
    request: UpdateWorkspaceRequest,
    _member=Depends(get_workspace_member),
    session: AsyncSession = Depends(),
) -> ApiResponse:
    """Update workspace details. Requires membership."""
    service = WorkspaceService(session)
    try:
        workspace = await service.update_workspace(workspace_id, request)
    except WorkspaceError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return ApiResponse(data=WorkspaceResponse.model_validate(workspace))
