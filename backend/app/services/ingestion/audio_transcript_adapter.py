"""HER AI — Audio Transcript & Voice Memo Ingestion Adapter.

Parses timestamped audio transcripts (VTT, SRT, Whisper JSON, and timestamped text)
preserving temporal playback offsets and speaker tags without audio synthesis or cloning.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.base import BaseIngestionAdapter, IngestedChunk
from app.services.ingestion.sanitization import sanitize_raw_text

# Regex for SRT / VTT timestamps: e.g. "00:01:20.000 --> 00:01:25.000" or "00:01:20,000 --> 00:01:25,000"
_TIMESTAMP_LINE_RE = re.compile(
    r"(\d{2}:\d{2}(?::\d{2})?(?:[.,]\d+)?)\s*-->\s*(\d{2}:\d{2}(?::\d{2})?(?:[.,]\d+)?)",
    re.IGNORECASE,
)
_TIMESTAMP_BRACKET_RE = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)$")


class AudioTranscriptAdapter(BaseIngestionAdapter):
    """Adapter for timestamped voice memo transcripts and audio text."""

    MAX_CHUNK_CHARS = 1800

    def extract_chunks(
        self,
        file_path: str,
        artifact: MemoryArtifact,
        context_notes: str | None = None,
    ) -> list[IngestedChunk]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Transcript file not found at: {file_path}")

        try:
            raw_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = path.read_text(encoding="latin-1")

        clean_text = sanitize_raw_text(raw_text)
        if not clean_text:
            return []

        source_created_at = (
            artifact.created_at
            if artifact.created_at
            else datetime.now(timezone.utc)
        )

        clean_context = sanitize_raw_text(context_notes or "")

        # 1. Attempt Whisper JSON parse
        if clean_text.startswith("{") and "segments" in clean_text:
            try:
                data = json.loads(clean_text)
                if isinstance(data, dict) and "segments" in data:
                    return self._process_whisper_json(
                        data["segments"],
                        artifact,
                        source_created_at,
                        clean_context,
                    )
            except json.JSONDecodeError:
                pass

        # 2. Attempt VTT / SRT parse
        if "-->" in clean_text:
            return self._process_vtt_srt(
                clean_text,
                artifact,
                source_created_at,
                clean_context,
            )

        # 3. Fallback: Parse bracketed timestamps e.g. [01:23] or plain transcript lines
        return self._process_bracketed_or_plain_text(
            clean_text,
            artifact,
            source_created_at,
            clean_context,
        )

    def _process_whisper_json(
        self,
        segments: list[dict],
        artifact: MemoryArtifact,
        source_created_at: datetime,
        context_notes: str,
    ) -> list[IngestedChunk]:
        chunks: list[IngestedChunk] = []
        current_texts: list[str] = []
        start_time: str | None = None
        end_time: str | None = None
        current_len = 0

        for seg in segments:
            text = sanitize_raw_text(str(seg.get("text", "")))
            if not text:
                continue
            seg_start = self._format_seconds(seg.get("start", 0))
            seg_end = self._format_seconds(seg.get("end", 0))

            if start_time is None:
                start_time = seg_start
            end_time = seg_end

            current_texts.append(f"[{seg_start}] {text}")
            current_len += len(text)

            if current_len >= self.MAX_CHUNK_CHARS:
                content = "\n".join(current_texts)
                if context_notes and not chunks:
                    content = f"Recording Context: {context_notes}\n\n{content}"
                loc = f"{start_time} - {end_time}"
                chunks.append(
                    IngestedChunk(
                        content=content,
                        source_location=loc,
                        source_type="audio",
                        source_created_at=source_created_at,
                        metadata={"start_time": start_time, "end_time": end_time},
                    )
                )
                current_texts = []
                start_time = None
                current_len = 0

        if current_texts:
            content = "\n".join(current_texts)
            if context_notes and not chunks:
                content = f"Recording Context: {context_notes}\n\n{content}"
            loc = f"{start_time or '00:00'} - {end_time or 'end'}"
            chunks.append(
                IngestedChunk(
                    content=content,
                    source_location=loc,
                    source_type="audio",
                    source_created_at=source_created_at,
                    metadata={"start_time": start_time, "end_time": end_time},
                )
            )

        return chunks

    def _process_vtt_srt(
        self,
        text: str,
        artifact: MemoryArtifact,
        source_created_at: datetime,
        context_notes: str,
    ) -> list[IngestedChunk]:
        chunks: list[IngestedChunk] = []
        lines = text.splitlines()

        current_texts: list[str] = []
        chunk_start: str | None = None
        chunk_end: str | None = None
        current_len = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Skip empty lines, sequence numbers, WEBVTT headers
            if not line or line.isdigit() or line.upper() == "WEBVTT":
                i += 1
                continue

            ts_match = _TIMESTAMP_LINE_RE.search(line)
            if ts_match:
                start_ts, end_ts = ts_match.group(1), ts_match.group(2)
                if chunk_start is None:
                    chunk_start = start_ts
                chunk_end = end_ts
                i += 1
                # Read subtitle text lines until blank line
                sub_text_parts = []
                while i < len(lines) and lines[i].strip() and not _TIMESTAMP_LINE_RE.search(lines[i]):
                    sub_text_parts.append(lines[i].strip())
                    i += 1
                combined = " ".join(sub_text_parts)
                if combined:
                    current_texts.append(f"[{start_ts}] {combined}")
                    current_len += len(combined)

                if current_len >= self.MAX_CHUNK_CHARS:
                    body = "\n".join(current_texts)
                    if context_notes and not chunks:
                        body = f"Recording Context: {context_notes}\n\n{body}"
                    chunks.append(
                        IngestedChunk(
                            content=body,
                            source_location=f"{chunk_start} - {chunk_end}",
                            source_type="audio",
                            source_created_at=source_created_at,
                            metadata={"start_time": chunk_start, "end_time": chunk_end},
                        )
                    )
                    current_texts = []
                    chunk_start = None
                    current_len = 0
            else:
                i += 1

        if current_texts:
            body = "\n".join(current_texts)
            if context_notes and not chunks:
                body = f"Recording Context: {context_notes}\n\n{body}"
            chunks.append(
                IngestedChunk(
                    content=body,
                    source_location=f"{chunk_start or '00:00'} - {chunk_end or 'end'}",
                    source_type="audio",
                    source_created_at=source_created_at,
                    metadata={"start_time": chunk_start, "end_time": chunk_end},
                )
            )

        return chunks

    def _process_bracketed_or_plain_text(
        self,
        text: str,
        artifact: MemoryArtifact,
        source_created_at: datetime,
        context_notes: str,
    ) -> list[IngestedChunk]:
        chunks: list[IngestedChunk] = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        current_group: list[str] = []
        current_len = 0
        first_loc: str | None = None
        last_loc: str | None = None
        part = 1

        for p in paragraphs:
            # Check for bracketed time
            m = _TIMESTAMP_BRACKET_RE.match(p)
            if m:
                if first_loc is None:
                    first_loc = m.group(1)
                last_loc = m.group(1)

            if current_len + len(p) > self.MAX_CHUNK_CHARS and current_group:
                body = "\n\n".join(current_group)
                if context_notes and part == 1:
                    body = f"Recording Context: {context_notes}\n\n{body}"
                loc = f"{first_loc} - {last_loc}" if (first_loc and last_loc) else f"Audio Part {part}"
                chunks.append(
                    IngestedChunk(
                        content=body,
                        source_location=loc,
                        source_type="audio",
                        source_created_at=source_created_at,
                        metadata={"part": part},
                    )
                )
                part += 1
                current_group = [p]
                current_len = len(p)
                first_loc = None
                last_loc = None
            else:
                current_group.append(p)
                current_len += len(p)

        if current_group:
            body = "\n\n".join(current_group)
            if context_notes and part == 1:
                body = f"Recording Context: {context_notes}\n\n{body}"
            loc = f"{first_loc} - {last_loc}" if (first_loc and last_loc) else (f"Audio Part {part}" if part > 1 else "Full Transcript")
            chunks.append(
                IngestedChunk(
                    content=body,
                    source_location=loc,
                    source_type="audio",
                    source_created_at=source_created_at,
                    metadata={"part": part},
                )
            )

        return chunks

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        s = int(seconds)
        m = s // 60
        s = s % 60
        h = m // 60
        m = m % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
