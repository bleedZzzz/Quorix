"""Quorix API — Workspace repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.workspace import Workspace, WorkspaceMember


class WorkspaceRepository:
    """Database operations for workspaces."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        """Get a workspace by ID."""
        result = await self._session.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Workspace | None:
        """Get a workspace by slug."""
        result = await self._session.execute(
            select(Workspace).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Workspace]:
        """List all workspaces the user is a member of."""
        result = await self._session.execute(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, workspace: Workspace) -> Workspace:
        """Insert a new workspace."""
        self._session.add(workspace)
        await self._session.flush()
        return workspace

    async def update(self, workspace: Workspace) -> Workspace:
        """Update an existing workspace."""
        await self._session.flush()
        return workspace

    async def slug_exists(self, slug: str) -> bool:
        """Check if a slug is already taken."""
        result = await self._session.execute(
            select(Workspace.id).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none() is not None

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        """Add a member to a workspace."""
        self._session.add(member)
        await self._session.flush()
        return member

    async def get_member(self, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
        """Get a workspace member."""
        result = await self._session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_member_count(self, workspace_id: UUID) -> int:
        """Get the number of members in a workspace."""
        result = await self._session.execute(
            select(func.count(WorkspaceMember.id)).where(
                WorkspaceMember.workspace_id == workspace_id
            )
        )
        return result.scalar_one()
