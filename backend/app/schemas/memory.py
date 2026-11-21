from uuid import UUID
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

MemoryType = Literal[
    "personal_info", "personality_trait", "communication_preference",
    "like", "dislike", "hobby", "interest", "career_goal", "dream", "ambition",
    "life_event", "relationship", "emotional_experience", "important_conversation",
    "daily_experience", "future_plan", "learning_progress", "milestone", "general"
]

ArtifactType = Literal["note", "letter", "document", "photo", "audio_transcript"]
TemporalPrecision = Literal["day", "month", "year", "decade", "unknown"]
MemoryStatus = Literal["active", "superseded", "disputed"]


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str = Field(min_length=1, max_length=5000)
    importance: int = Field(default=3, ge=1, le=5)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    event_date: str | None = None
    event_date_precision: TemporalPrecision = "unknown"
    metadata: dict | None = None


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    importance: int | None = Field(default=None, ge=1, le=5)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None
    metadata: dict | None = None


class MemoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    memory_type: str
    content: str
    importance: int
    confidence: float
    is_active: bool
    event_date: date | None = None
    event_date_precision: str = "unknown"
    source_created_at: datetime | None = None
    status: str = "active"
    superseded_by_id: UUID | None = None
    access_scope: str = "default"
    version: int = 1
    memory_metadata: dict | None = None
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class MemoryListResponse(BaseModel):
    memories: list[MemoryResponse]
    total: int


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=50)
    min_similarity: float = Field(default=0.20, ge=0.0, le=1.0)


class MemorySearchResult(BaseModel):
    id: str
    content: str
    memory_type: str
    importance: int
    confidence: float
    similarity: float
    event_date: str | None = None
    event_date_precision: str = "unknown"
    status: str = "active"


class MemorySearchResponse(BaseModel):
    results: list[MemorySearchResult]
    query: str
    total: int


class MemoryExportResponse(BaseModel):
    user_id: UUID
    total_memories: int
    memories: list[MemoryResponse]
    exported_at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 12 Phase 3 Ingestion & Job Schemas
# ──────────────────────────────────────────────────────────────────────────────

class TextIngestRequest(BaseModel):
    title: str = Field(default="Untitled Note", min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=100_000)
    artifact_type: ArtifactType = "note"
    context_notes: str | None = Field(default=None, max_length=5000)


class MemoryArtifactJobResponse(BaseModel):
    job_id: UUID
    status: str
    artifact_type: str
    filename: str
    file_size_bytes: int
    checksum_sha256: str
    retry_count: int = 0
    created_at: datetime
    message: str


class MemoryArtifactJobDetailResponse(BaseModel):
    job_id: UUID
    user_id: UUID
    status: str
    artifact_type: str
    filename: str
    file_size_bytes: int
    checksum_sha256: str
    retry_count: int = 0
    error_message: str | None = None
    context_notes: str | None = None
    created_at: datetime
    processed_at: datetime | None = None
    extracted_memories_count: int = 0
    extracted_memory_ids: list[UUID] = []


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 12 Phase 3 Provenance & Correction Schemas
# ──────────────────────────────────────────────────────────────────────────────

class ArtifactProvenanceInfo(BaseModel):
    artifact_id: UUID
    filename: str
    artifact_type: str
    checksum_sha256: str


class MemorySourceInfo(BaseModel):
    source_id: UUID
    source_type: str
    source_location: str | None = None
    excerpt: str | None = None
    created_at: datetime
    artifact: ArtifactProvenanceInfo | None = None


class MemoryHistoryEntry(BaseModel):
    memory_id: UUID
    version: int
    status: str
    is_active: bool
    created_at: datetime
    superseded_at: str | None = None
    superseded_reason: str | None = None


class MemoryProvenanceResponse(BaseModel):
    memory_id: UUID
    content: str
    memory_type: str
    importance: int
    confidence: float
    event_date: date | None = None
    event_date_precision: str = "unknown"
    version: int
    status: str
    superseded_by_id: UUID | None = None
    sources: list[MemorySourceInfo] = []
    history: list[MemoryHistoryEntry] = []


class MemoryCorrectionRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    memory_type: MemoryType | None = None
    importance: int | None = Field(default=None, ge=1, le=5)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    event_date: str | None = None
    event_date_precision: TemporalPrecision | None = None
    reason: str = Field(min_length=1, max_length=1000)


class MemoryCorrectionResponse(BaseModel):
    success: bool
    old_memory: MemoryResponse
    new_memory: MemoryResponse
    correction_reason: str


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 12 Phase 3 Timeline Schemas
# ──────────────────────────────────────────────────────────────────────────────

class MemoryTimelineItem(BaseModel):
    id: UUID
    content: str
    memory_type: str
    importance: int
    confidence: float
    event_date: date | None = None
    event_date_precision: str = "unknown"
    formatted_date: str
    source_created_at: datetime | None = None
    status: str
    version: int
    primary_source_type: str = "general"
    primary_source_location: str | None = None


class MemoryTimelineResponse(BaseModel):
    items: list[MemoryTimelineItem]
    total: int
    limit: int
    offset: int
