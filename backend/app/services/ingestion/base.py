"""HER AI — Ingestion Adapter Base Interface & Chunk Model.

Defines the contract for multi-source ingestion adapters:
  - IngestedChunk: Normalized slice of text with location and temporal metadata.
  - BaseIngestionAdapter: Protocol for converting artifacts into chunks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.models.memory_artifact import MemoryArtifact


@dataclass
class IngestedChunk:
    """A distinct semantic or structural chunk extracted from a source artifact."""

    content: str
    source_location: str  # e.g., "Page 3", "01:15 - 01:45", "EXIF / Capture Metadata"
    source_type: str  # "document", "note", "letter", "photo", "audio"
    source_created_at: datetime | None = None
    suggested_event_date: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseIngestionAdapter(ABC):
    """Abstract base class for all memory ingestion adapters."""

    @abstractmethod
    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        """
        Extract normalized chunks and structural metadata from the file.

        Args:
            file_path: Local filesystem path to the uploaded file.
            artifact: The parent MemoryArtifact database record.
            context_notes: Optional user-supplied context or annotation.

        Returns:
            List of IngestedChunk objects ready for memory fact extraction.
        """
        raise NotImplementedError
