"""Section detector identifying hierarchical academic paper sections."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.application.ingestion.pdf_parser import ExtractedPage


@dataclass
class DetectedSection:
    title: str
    section_type: str  # abstract, introduction, method, results, discussion, conclusion, references, other
    start_page: int
    end_page: int
    level: int = 1
    order_index: int = 0


class SectionDetector:
    """Detects canonical academic paper sections and hierarchy from parsed pages."""

    PATTERNS = [
        ("abstract", re.compile(r"^\s*(abstract|executive summary)\b", re.IGNORECASE)),
        ("introduction", re.compile(r"^\s*(1\.?\s*)?introduction\b", re.IGNORECASE)),
        ("related_work", re.compile(r"^\s*([0-9]\.?\s*)?(related work|background|literature review)\b", re.IGNORECASE)),
        ("method", re.compile(r"^\s*([0-9]\.?\s*)?(methodology|methods|method|proposed model|approach|system architecture)\b", re.IGNORECASE)),
        ("results", re.compile(r"^\s*([0-9]\.?\s*)?(results|experiments|experimental evaluation|evaluation)\b", re.IGNORECASE)),
        ("discussion", re.compile(r"^\s*([0-9]\.?\s*)?(discussion|analysis|ablation study)\b", re.IGNORECASE)),
        ("conclusion", re.compile(r"^\s*([0-9]\.?\s*)?(conclusion|concluding remarks|future work)\b", re.IGNORECASE)),
        ("references", re.compile(r"^\s*([0-9]\.?\s*)?(references|bibliography|works cited)\b", re.IGNORECASE)),
    ]

    def detect_sections(self, pages: list[ExtractedPage]) -> list[DetectedSection]:
        sections: list[DetectedSection] = []
        current_section: DetectedSection | None = None
        order = 0

        for page in pages:
            lines = page.text.split("\n")
            for line in lines:
                stripped = line.strip()
                if not stripped or len(stripped) > 80:
                    continue

                for sec_type, regex in self.PATTERNS:
                    if regex.search(stripped):
                        if current_section:
                            current_section.end_page = max(current_section.start_page, page.page_number)
                        current_section = DetectedSection(
                            title=stripped,
                            section_type=sec_type,
                            start_page=page.page_number,
                            end_page=page.page_number,
                            level=1,
                            order_index=order,
                        )
                        sections.append(current_section)
                        order += 1
                        break

        # Ensure last section end page is set to final page
        if current_section and pages:
            current_section.end_page = pages[-1].page_number

        # If no sections were detected, create a fallback full-document section
        if not sections and pages:
            sections.append(
                DetectedSection(
                    title="Main Document",
                    section_type="body",
                    start_page=1,
                    end_page=pages[-1].page_number,
                    level=1,
                    order_index=0,
                )
            )

        return sections
