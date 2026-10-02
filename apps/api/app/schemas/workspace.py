"""Workspace Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.auth import UserResponse


class CreateWorkspaceRequest(BaseModel):
    """Request to create a new workspace."""
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None


class UpdateWorkspaceRequest(BaseModel):
    """Request to update a workspace."""
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


WorkspaceCreateRequest = CreateWorkspaceRequest
WorkspaceUpdateRequest = UpdateWorkspaceRequest


class WorkspaceMemberResponse(BaseModel):
    """Workspace member representation."""
    id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    user: UserResponse | None = None

    model_config = {"from_attributes": True}


class WorkspaceResponse(BaseModel):
    """Workspace representation."""
    id: UUID
    name: str
    slug: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    member_count: int | None = None

    model_config = {"from_attributes": True}


class WorkspaceDetailResponse(WorkspaceResponse):
    """Workspace with members."""
    members: list[WorkspaceMemberResponse] = []
