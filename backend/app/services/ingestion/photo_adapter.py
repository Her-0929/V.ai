"""HER AI — Photo Context & Image Metadata Ingestion Adapter.

Extracts EXIF capture date, camera tags, and contextual descriptions from photos.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ExifTags

from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.base import BaseIngestionAdapter, IngestedChunk
from app.services.ingestion.sanitization import sanitize_raw_text

logger = logging.getLogger(__name__)


class PhotoContextAdapter(BaseIngestionAdapter):
    """Adapter for ingesting photos with EXIF capture dates and contextual descriptions."""

    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Photo file not found at: {file_path}")

        meta: dict[str, Any] = {
            "format": path.suffix.lower().lstrip("."),
            "filename": path.name,
        }
        suggested_event_date: str | None = None
        source_created_at: datetime | None = None

        try:
            with Image.open(str(path)) as img:
                meta["width"], meta["height"] = img.size
                exif_data = img._getexif() if hasattr(img, "_getexif") else None

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                            # EXIF date format is usually "YYYY:MM:DD HH:MM:SS"
                            meta["exif_datetime_raw"] = str(value)
                            try:
                                dt = datetime.strptime(str(value).strip(), "%Y:%m:%d %H:%M:%S")
                                source_created_at = dt.replace(tzinfo=timezone.utc)
                                suggested_event_date = dt.strftime("%Y-%m-%d")
                            except (ValueError, TypeError):
                                pass
                        elif tag_name in ("Make", "Model"):
                            meta[tag_name.lower()] = str(value).strip()
        except Exception as exc:
            logger.warning("Could not parse EXIF from image %s: %s", file_path, exc)

        clean_notes = sanitize_raw_text(context_notes or "")

        # Assemble descriptive biographical text from contextual notes and metadata
        lines = [f"Photo Artifact: {path.name}"]
        if suggested_event_date:
            lines.append(f"Capture Date (from EXIF): {suggested_event_date}")
        if "make" in meta and "model" in meta:
            lines.append(f"Camera: {meta['make']} {meta['model']}")
        if clean_notes:
            lines.append(f"Contextual Description / Annotation:\n{clean_notes}")
        else:
            lines.append("Contextual Description: Personal photograph without additional user annotation.")

        chunk_content = "\n".join(lines)

        return [
            IngestedChunk(
                content=chunk_content,
                source_location="Photo EXIF & Context",
                source_type="photo",
                source_created_at=source_created_at,
                suggested_event_date=suggested_event_date,
                metadata=meta,
            )
        ]
