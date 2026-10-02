"""Notes, annotations, and tagging service."""

from __future__ import annotations

import uuid
from typing import Any

from app.infrastructure.database.models.notes import Annotation, Note, Tag
from app.infrastructure.repositories.notes_repository import NotesRepository


class NoteService:
    """Manages markdown research notes, wiki backlinks, PDF annotations, and tags."""

    def __init__(self, notes_repo: NotesRepository) -> None:
        self.repo = notes_repo

    async def create_note(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        content: str = "",
        paper_id: uuid.UUID | None = None,
        folder: str = "/",
    ) -> Note:
        note = await self.repo.create_note(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            content=content,
            paper_id=paper_id,
            folder=folder,
        )
        return note

    async def get_note(self, note_id: uuid.UUID, workspace_id: uuid.UUID) -> Note | None:
        return await self.repo.get_note(note_id, workspace_id)

    async def list_notes(
        self,
        workspace_id: uuid.UUID,
        paper_id: uuid.UUID | None = None,
        folder: str | None = None,
    ) -> list[Note]:
        return await self.repo.list_notes(workspace_id=workspace_id, paper_id=paper_id, folder=folder)

    async def update_note(
        self,
        note_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str | None = None,
        content: str | None = None,
        folder: str | None = None,
    ) -> Note | None:
        return await self.repo.update_note(
            note_id=note_id,
            workspace_id=workspace_id,
            title=title,
            content=content,
            folder=folder,
        )

    async def delete_note(self, note_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        return await self.repo.delete_note(note_id, workspace_id)

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
        return await self.repo.create_annotation(
            document_id=document_id,
            user_id=user_id,
            page_number=page_number,
            highlight_text=highlight_text,
            annotation_text=annotation_text,
            color=color,
            position_data=position_data,
        )

    async def list_annotations(self, document_id: uuid.UUID) -> list[Annotation]:
        return await self.repo.list_annotations(document_id)

    async def create_tag(self, workspace_id: uuid.UUID, name: str, color: str | None = None) -> Tag:
        return await self.repo.create_tag(workspace_id=workspace_id, name=name, color=color)

    async def list_tags(self, workspace_id: uuid.UUID) -> list[Tag]:
        return await self.repo.list_tags(workspace_id)
