"""Conversation and Message repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.conversation import Conversation, Message
from app.infrastructure.database.models.evidence import Claim


class ConversationRepository:
    """Repository handling CRUD for research conversations and message history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = "New Research Session",
        scope_type: str = "workspace",
        scope_ids: list[uuid.UUID] | None = None,
    ) -> Conversation:
        conversation = Conversation(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            scope_type=scope_type,
            scope_ids=scope_ids or [],
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_by_id(
        self,
        conversation_id: uuid.UUID,
        workspace_id: uuid.UUID | None = None,
    ) -> Conversation | None:
        stmt = (
            select(Conversation)
            .options(
                selectinload(Conversation.messages)
                .selectinload(Message.claims)
                .selectinload(Claim.evidence_spans),
                selectinload(Conversation.messages)
                .selectinload(Message.claims)
                .selectinload(Claim.citations),
            )
            .where(Conversation.id == conversation_id)
        )
        if workspace_id:
            stmt = stmt.where(Conversation.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_conversations(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.workspace_id == workspace_id)
        )
        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)
        stmt = stmt.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_title(self, conversation_id: uuid.UUID, title: str) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        conversation = result.scalars().first()
        if conversation:
            conversation.title = title
            await self.session.flush()
        return conversation

    async def delete(self, conversation_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        stmt = delete(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.workspace_id == workspace_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_=metadata or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 100,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .options(
                selectinload(Message.claims).selectinload(Claim.evidence_spans),
                selectinload(Message.claims).selectinload(Claim.citations),
            )
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
