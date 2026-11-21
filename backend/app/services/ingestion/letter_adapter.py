"""HER AI — Personal Letter Ingestion Adapter.

Extracts personal letters, correspondence, and journal entries,
detecting salutations, signoffs, and letter header dates.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.base import BaseIngestionAdapter, IngestedChunk
from app.services.ingestion.sanitization import sanitize_raw_text

# Common date headers in letters (e.g., "October 14, 2020", "15 August 2019", "2021-04-12")
_DATE_LINE_RE = re.compile(
    r"(?:Date:\s*)?([A-Za-z]+ \d{1,2},? \d{4}|\d{1,2} [A-Za-z]+ \d{4}|\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)
_SALUTATION_RE = re.compile(r"^(Dear|Dearest|To my dearest|Hello|My dear)\s+([^,\n]+),?", re.IGNORECASE | re.MULTILINE)
_SIGNOFF_RE = re.compile(r"(With love|Love always|Yours truly|Yours|Warmly|Always|Sincerely),?\s*\n+([^\n]+)$", re.IGNORECASE)


class PersonalLetterAdapter(BaseIngestionAdapter):
    """Adapter specialized for personal letters and heartfelt correspondences."""

    MAX_CHUNK_CHARS = 2000

    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Letter file not found at: {file_path}")

        try:
            raw_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = path.read_text(encoding="latin-1")

        clean_text = sanitize_raw_text(raw_text)
        if not clean_text:
            return []

        # Analyze letter structure
        suggested_date: str | None = None
        recipient: str | None = None
        sender: str | None = None

        # Look for date in first 5 lines
        first_lines = "\n".join(clean_text.splitlines()[:5])
        date_match = _DATE_LINE_RE.search(first_lines)
        if date_match:
            suggested_date = date_match.group(1).strip()

        # Look for salutation
        sal_match = _SALUTATION_RE.search(clean_text)
        if sal_match:
            recipient = sal_match.group(2).strip()

        # Look for signoff
        sign_match = _SIGNOFF_RE.search(clean_text)
        if sign_match:
            sender = sign_match.group(2).strip()

        meta: dict[str, Any] = {
            "is_letter": True,
            "recipient": recipient,
            "sender": sender,
            "letter_date_raw": suggested_date,
        }

        source_created_at = (
            artifact.created_at
            if artifact.created_at
            else datetime.now(timezone.utc)
        )

        clean_context = sanitize_raw_text(context_notes or "")

        # Chunk paragraphs
        paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
        chunks: list[IngestedChunk] = []
        current_group: list[str] = []
        current_len = 0
        part = 1

        for idx, p in enumerate(paragraphs, start=1):
            if current_len + len(p) > self.MAX_CHUNK_CHARS and current_group:
                body = "\n\n".join(current_group)
                if clean_context and part == 1:
                    body = f"Letter Context: {clean_context}\n\n{body}"
                chunks.append(
                    IngestedChunk(
                        content=body,
                        source_location=f"Letter Part {part}",
                        source_type="letter",
                        source_created_at=source_created_at,
                        suggested_event_date=suggested_date,
                        metadata={**meta, "part": part},
                    )
                )
                part += 1
                current_group = [p]
                current_len = len(p)
            else:
                current_group.append(p)
                current_len += len(p)

        if current_group:
            body = "\n\n".join(current_group)
            if clean_context and part == 1:
                body = f"Letter Context: {clean_context}\n\n{body}"
            chunks.append(
                IngestedChunk(
                    content=body,
                    source_location=f"Letter Part {part}" if part > 1 else "Full Letter",
                    source_type="letter",
                    source_created_at=source_created_at,
                    suggested_event_date=suggested_date,
                    metadata={**meta, "part": part},
                )
            )

        return chunks
