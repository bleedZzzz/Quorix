"""Quorix API — Semantic chunker preserving document paragraphs and section boundaries."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from app.application.ingestion.pdf_parser import ExtractedPage
from app.application.ingestion.section_detector import DetectedSection


@dataclass
class SemanticChunk:
    page_number: int
    chunk_index: int
    content: str
    token_count: int
    start_offset: int
    end_offset: int
    text_hash: str
    section_title: str | None = None
    section_type: str | None = None
    metadata: dict[str, Any] | None = None


class SemanticChunker:
    """Chunks text into coherent passages respecting paragraph boundaries and section scopes."""

    def __init__(self, target_chunk_size: int = 400, chunk_overlap: int = 50) -> None:
        self.target_chunk_size = target_chunk_size  # Approx words/tokens
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        pages: list[ExtractedPage],
        sections: list[DetectedSection],
    ) -> list[SemanticChunk]:
        chunks: list[SemanticChunk] = []
        global_chunk_idx = 0

        for page in pages:
            # Find active section for this page
            active_section = None
            for sec in sections:
                if sec.start_page <= page.page_number <= sec.end_page:
                    active_section = sec
                    break

            page_text = page.text
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page_text) if p.strip()]

            current_chunk_words: list[str] = []
            current_start_offset = 0

            for para in paragraphs:
                words = para.split()
                if not words:
                    continue

                if len(current_chunk_words) + len(words) > self.target_chunk_size and current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    text_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                    chunks.append(
                        SemanticChunk(
                            page_number=page.page_number,
                            chunk_index=global_chunk_idx,
                            content=chunk_text,
                            token_count=len(current_chunk_words),
                            start_offset=current_start_offset,
                            end_offset=current_start_offset + len(chunk_text),
                            text_hash=text_hash,
                            section_title=active_section.title if active_section else None,
                            section_type=active_section.section_type if active_section else None,
                        )
                    )
                    global_chunk_idx += 1
                    current_start_offset += len(chunk_text)
                    # Keep overlap
                    current_chunk_words = current_chunk_words[-self.chunk_overlap :]

                current_chunk_words.extend(words)

            if current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                text_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                chunks.append(
                    SemanticChunk(
                        page_number=page.page_number,
                        chunk_index=global_chunk_idx,
                        content=chunk_text,
                        token_count=len(current_chunk_words),
                        start_offset=current_start_offset,
                        end_offset=current_start_offset + len(chunk_text),
                        text_hash=text_hash,
                        section_title=active_section.title if active_section else None,
                        section_type=active_section.section_type if active_section else None,
                    )
                )
                global_chunk_idx += 1

        return chunks
