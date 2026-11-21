"""HER AI — Plain-Text & Markdown Note Ingestion Adapter.

Extracts content from plain-text notes, journal logs, and Markdown documents
with heading-level or paragraph-level provenance.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.base import BaseIngestionAdapter, IngestedChunk
from app.services.ingestion.sanitization import sanitize_raw_text

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_DATE_FRONTMATTER_RE = re.compile(r"^date:\s*[\"']?([0-9\-/]+)[\"']?", re.IGNORECASE | re.MULTILINE)


class TextNoteAdapter(BaseIngestionAdapter):
    """Adapter for plain-text notes and Markdown files."""

    MAX_CHUNK_CHARS = 2000

    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Note file not found at: {file_path}")

        try:
            raw_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            raw_text = path.read_text(encoding="latin-1")

        clean_text = sanitize_raw_text(raw_text)
        if not clean_text:
            return []

        # Check for frontmatter date
        suggested_event_date: str | None = None
        date_match = _DATE_FRONTMATTER_RE.search(clean_text)
        if date_match:
            suggested_event_date = date_match.group(1).strip()

        source_created_at = (
            artifact.created_at
            if artifact.created_at
            else datetime.now(timezone.utc)
        )

        clean_context = sanitize_raw_text(context_notes or "")

        # Check if Markdown headers exist
        sections = list(_HEADING_RE.finditer(clean_text))
        chunks: list[IngestedChunk] = []

        if sections:
            # Chunk by headings
            prev_end = 0
            current_title = "Introduction / Preface"

            for i, match in enumerate(sections):
                start = match.start()
                if start > prev_end:
                    section_body = clean_text[prev_end:start].strip()
                    if section_body:
                        if clean_context and not chunks:
                            section_body = f"Context Notes: {clean_context}\n\n{section_body}"
                        chunks.append(
                            IngestedChunk(
                                content=section_body,
                                source_location=f"Section: {current_title}",
                                source_type="note",
                                source_created_at=source_created_at,
                                suggested_event_date=suggested_event_date,
                                metadata={"title": current_title},
                            )
                        )
                current_title = match.group(2).strip()
                prev_end = match.end()

            # Last section
            if prev_end < len(clean_text):
                section_body = clean_text[prev_end:].strip()
                if section_body:
                    chunks.append(
                        IngestedChunk(
                            content=section_body,
                            source_location=f"Section: {current_title}",
                            source_type="note",
                            source_created_at=source_created_at,
                            suggested_event_date=suggested_event_date,
                            metadata={"title": current_title},
                        )
                    )
        else:
            # Chunk by paragraphs
            paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
            current_group: list[str] = []
            current_len = 0
            group_idx = 1

            for p in paragraphs:
                if current_len + len(p) > self.MAX_CHUNK_CHARS and current_group:
                    body = "\n\n".join(current_group)
                    if clean_context and group_idx == 1:
                        body = f"Context Notes: {clean_context}\n\n{body}"
                    chunks.append(
                        IngestedChunk(
                            content=body,
                            source_location=f"Paragraph Group {group_idx}",
                            source_type="note",
                            source_created_at=source_created_at,
                            suggested_event_date=suggested_event_date,
                            metadata={"group_index": group_idx},
                        )
                    )
                    group_idx += 1
                    current_group = [p]
                    current_len = len(p)
                else:
                    current_group.append(p)
                    current_len += len(p)

            if current_group:
                body = "\n\n".join(current_group)
                if clean_context and group_idx == 1:
                    body = f"Context Notes: {clean_context}\n\n{body}"
                chunks.append(
                    IngestedChunk(
                        content=body,
                        source_location=f"Paragraph Group {group_idx}" if group_idx > 1 else "Note Body",
                        source_type="note",
                        source_created_at=source_created_at,
                        suggested_event_date=suggested_event_date,
                        metadata={"group_index": group_idx},
                    )
                )

        return chunks
