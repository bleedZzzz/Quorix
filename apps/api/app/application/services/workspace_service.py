"""Workspace service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.workspace import Workspace, WorkspaceMember
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import CreateWorkspaceRequest, UpdateWorkspaceRequest


class WorkspaceError(Exception):
    """Raised when a workspace operation fails."""


class WorkspaceService:
    """Application service for workspace workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = WorkspaceRepository(session)

    async def create_workspace(
        self, request: CreateWorkspaceRequest, owner_id: UUID
    ) -> Workspace:
        """Create a new workspace and add the owner as a member."""
        if await self._repo.slug_exists(request.slug):
            raise WorkspaceError(f"Slug '{request.slug}' is already taken")

        workspace = Workspace(
            name=request.name,
            slug=request.slug,
            description=request.description,
            owner_id=owner_id,
        )
        workspace = await self._repo.create(workspace)

        # Add owner as the first member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role="owner",
        )
        await self._repo.add_member(member)

        return workspace

    async def get_workspace(self, workspace_id: UUID) -> Workspace:
        """Get a workspace by ID."""
        workspace = await self._repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceError("Workspace not found")
        return workspace

    async def list_user_workspaces(self, user_id: UUID) -> list[Workspace]:
        """List all workspaces for a user."""
        return await self._repo.list_for_user(user_id)

    async def update_workspace(
        self,
        workspace_id: UUID,
        request: UpdateWorkspaceRequest,
    ) -> Workspace:
        """Update workspace details."""
        workspace = await self._repo.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceError("Workspace not found")

        if request.name is not None:
            workspace.name = request.name
        if request.description is not None:
            workspace.description = request.description

        return await self._repo.update(workspace)
