"""Quorix API — PDF parsing engine using PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pymupdf


@dataclass
class ExtractedPage:
    page_number: int
    text: str
    width: float
    height: float
    blocks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ParsedPDF:
    page_count: int
    metadata: dict[str, Any]
    pages: list[ExtractedPage]
    raw_text: str


class PDFParser:
    """Extracts structured text, page metrics, and visual layout blocks from PDF documents."""

    def parse_bytes(self, pdf_bytes: bytes) -> ParsedPDF:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        meta = doc.metadata or {}

        extracted_pages: list[ExtractedPage] = []
        full_text_parts: list[str] = []

        for page_idx in range(page_count):
            page = doc[page_idx]
            rect = page.rect
            text = page.get_text("text")
            full_text_parts.append(text)

            # Extract detailed block structures (text blocks, coordinates, font info)
            blocks_raw = page.get_text("blocks")
            blocks: list[dict[str, Any]] = []
            for b in blocks_raw:
                if len(b) >= 5 and b[4]:  # b[4] is text string
                    blocks.append(
                        {
                            "bbox": [b[0], b[1], b[2], b[3]],
                            "text": b[4],
                            "type": b[5] if len(b) > 5 else 0,
                        }
                    )

            extracted_pages.append(
                ExtractedPage(
                    page_number=page_idx + 1,
                    text=text,
                    width=rect.width,
                    height=rect.height,
                    blocks=blocks,
                )
            )

        doc.close()

        return ParsedPDF(
            page_count=page_count,
            metadata=meta,
            pages=extracted_pages,
            raw_text="\n\n".join(full_text_parts),
        )
