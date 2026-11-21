"""HER AI — PDF Document Ingestion Adapter.

Extracts page-by-page text, document metadata, and structural locations from PDF files.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.base import BaseIngestionAdapter, IngestedChunk
from app.services.ingestion.sanitization import sanitize_raw_text

logger = logging.getLogger(__name__)


class PDFDocumentAdapter(BaseIngestionAdapter):
    """Adapter for ingesting PDF documents with page-level provenance."""

    MAX_CHUNK_CHARS = 2500  # ~500-600 tokens

    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            logger.exception("Failed to open PDF %s: %s", file_path, exc)
            raise ValueError(f"Corrupt or unreadable PDF document: {exc}") from exc

        # Extract PDF metadata if present
        meta: dict[str, Any] = {}
        source_created_at: datetime | None = None
        if reader.metadata:
            meta = {
                "title": reader.metadata.title,
                "author": reader.metadata.author,
                "producer": reader.metadata.producer,
            }
            creation_date = reader.metadata.creation_date
            if creation_date:
                # pypdf converts creation_date to datetime if parsed
                if isinstance(creation_date, datetime):
                    source_created_at = (
                        creation_date.astimezone(timezone.utc)
                        if creation_date.tzinfo
                        else creation_date.replace(tzinfo=timezone.utc)
                    )

        chunks: list[IngestedChunk] = []

        # If user provided context notes for the overall document, include as initial context
        clean_context = sanitize_raw_text(context_notes or "")

        for idx, page in enumerate(reader.pages, start=1):
            raw_page_text = page.extract_text() or ""
            clean_page_text = sanitize_raw_text(raw_page_text)
            if not clean_page_text:
                continue

            # Split large pages if necessary
            if len(clean_page_text) <= self.MAX_CHUNK_CHARS:
                page_content = clean_page_text
                if clean_context and idx == 1:
                    page_content = f"Document Context: {clean_context}\n\n{page_content}"

                chunks.append(
                    IngestedChunk(
                        content=page_content,
                        source_location=f"Page {idx}",
                        source_type="document",
                        source_created_at=source_created_at,
                        metadata={**meta, "page_number": idx, "total_pages": len(reader.pages)},
                    )
                )
            else:
                # Sub-chunk by paragraphs
                paragraphs = clean_page_text.split("\n\n")
                current_sub: list[str] = []
                current_len = 0
                part = 1

                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if current_len + len(para) > self.MAX_CHUNK_CHARS and current_sub:
                        sub_text = "\n\n".join(current_sub)
                        chunks.append(
                            IngestedChunk(
                                content=sub_text,
                                source_location=f"Page {idx} (Part {part})",
                                source_type="document",
                                source_created_at=source_created_at,
                                metadata={
                                    **meta,
                                    "page_number": idx,
                                    "part": part,
                                    "total_pages": len(reader.pages),
                                },
                            )
                        )
                        part += 1
                        current_sub = [para]
                        current_len = len(para)
                    else:
                        current_sub.append(para)
                        current_len += len(para)

                if current_sub:
                    sub_text = "\n\n".join(current_sub)
                    chunks.append(
                        IngestedChunk(
                            content=sub_text,
                            source_location=f"Page {idx} (Part {part})" if part > 1 else f"Page {idx}",
                            source_type="document",
                            source_created_at=source_created_at,
                            metadata={
                                **meta,
                                "page_number": idx,
                                "part": part,
                                "total_pages": len(reader.pages),
                            },
                        )
                    )

        return chunks
