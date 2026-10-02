"""Notes, annotations, and tags repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.notes import (
    Annotation,
    Note,
    NoteLink,
    PaperTag,
    Tag,
)


class NotesRepository:
    """Repository handling research notes, PDF annotations, tags, and graph backlinks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Notes
    async def create_note(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        content: str = "",
        paper_id: uuid.UUID | None = None,
        folder: str = "/",
    ) -> Note:
        note = Note(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            content=content,
            paper_id=paper_id,
            folder=folder,
        )
        self.session.add(note)
        await self.session.flush()
        return note

    async def get_note(self, note_id: uuid.UUID, workspace_id: uuid.UUID) -> Note | None:
        stmt = (
            select(Note)
            .options(selectinload(Note.paper))
            .where(Note.id == note_id, Note.workspace_id == workspace_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_notes(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID | None = None,
        folder: str | None = None,
    ) -> list[Note]:
        stmt = select(Note).where(Note.workspace_id == workspace_id)
        if paper_id:
            stmt = stmt.where(Note.paper_id == paper_id)
        if folder:
            stmt = stmt.where(Note.folder == folder)
        stmt = stmt.order_by(Note.updated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_note(
        self,
        note_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str | None = None,
        content: str | None = None,
        folder: str | None = None,
    ) -> Note | None:
        note = await self.get_note(note_id, workspace_id)
        if not note:
            return None
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if folder is not None:
            note.folder = folder
        await self.session.flush()
        return note

    async def delete_note(self, note_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        stmt = delete(Note).where(Note.id == note_id, Note.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # Backlinks
    async def add_note_link(
        self,
        source_note_id: uuid.UUID,
        target_note_id: uuid.UUID,
        link_type: str = "reference",
    ) -> NoteLink:
        link = NoteLink(
            source_note_id=source_note_id,
            target_note_id=target_note_id,
            link_type=link_type,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_backlinks(self, note_id: uuid.UUID) -> list[Note]:
        stmt = (
            select(Note)
            .join(NoteLink, NoteLink.source_note_id == Note.id)
            .where(NoteLink.target_note_id == note_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Annotations
    async def create_annotation(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        page_number: int,
        highlight_text: str | None = None,
        annotation_text: str | None = None,
        color: str = "#facc15",
        position_data: dict[str, Any] | None = None,
    ) -> Annotation:
        annotation = Annotation(
            document_id=document_id,
            user_id=user_id,
            page_number=page_number,
            highlight_text=highlight_text,
            annotation_text=annotation_text,
            color=color,
            position_data=position_data,
        )
        self.session.add(annotation)
        await self.session.flush()
        return annotation

    async def list_annotations(self, document_id: uuid.UUID) -> list[Annotation]:
        stmt = (
            select(Annotation)
            .where(Annotation.document_id == document_id)
            .order_by(Annotation.page_number.asc(), Annotation.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_annotation(self, annotation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = delete(Annotation).where(
            Annotation.id == annotation_id,
            Annotation.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # Tags
    async def create_tag(self, workspace_id: uuid.UUID, name: str, color: str | None = None) -> Tag:
        tag = Tag(workspace_id=workspace_id, name=name, color=color or "#6366f1")
        self.session.add(tag)
        await self.session.flush()
        return tag

    async def list_tags(self, workspace_id: uuid.UUID) -> list[Tag]:
        stmt = select(Tag).where(Tag.workspace_id == workspace_id).order_by(Tag.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def tag_paper(self, paper_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        pt = PaperTag(paper_id=paper_id, tag_id=tag_id)
        self.session.add(pt)
        await self.session.flush()

    async def untag_paper(self, paper_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        stmt = delete(PaperTag).where(PaperTag.paper_id == paper_id, PaperTag.tag_id == tag_id)
        await self.session.execute(stmt)
