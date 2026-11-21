"""HER AI — Memory Management REST API Endpoints (Milestone 11 Hardened)

Provides full CRUD, semantic search, export, and deactivation for user memories.
All endpoints strictly enforce authenticated user identity and rate limits.
"""

import logging
from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rate_limit import limiter
from app.core.config import settings
from app.models.memory import Memory
from app.models.memory_artifact import MemoryArtifact
from app.models.memory_source import MemorySource
from app.models.user import User
from app.schemas.memory import (
    ArtifactType,
    MemoryArtifactJobDetailResponse,
    MemoryArtifactJobResponse,
    MemoryCorrectionRequest,
    MemoryCorrectionResponse,
    MemoryCreate,
    MemoryExportResponse,
    MemoryListResponse,
    MemoryProvenanceResponse,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
    MemoryTimelineItem,
    MemoryTimelineResponse,
    MemoryUpdate,
    TextIngestRequest,
)
from app.services.ingestion.worker import job_worker
from app.services.memory_service import memory_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/memories",
    tags=["Memories"],
)


@router.get("", response_model=MemoryListResponse)
def list_memories(
    memory_type: str | None = Query(default=None, description="Filter by memory type"),
    is_active: bool = Query(default=True, description="Filter by active status"),
    limit: int = Query(default=50, ge=1, le=100, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryListResponse:
    """List memories for authenticated user with optional filtering by type and active status."""
    user_id = current_user.id

    count_stmt = select(func.count()).select_from(Memory).where(
        Memory.user_id == user_id,
        Memory.is_active == is_active,
    )
    if memory_type:
        count_stmt = count_stmt.where(Memory.memory_type == memory_type)

    total = db.scalar(count_stmt) or 0

    memories = memory_service.list_memories(
        db=db,
        user_id=user_id,
        memory_type=memory_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    return MemoryListResponse(
        memories=memories,
        total=total,
    )


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryResponse:
    """Create a new memory with vector embedding for authenticated user."""
    user_id = current_user.id

    try:
        memory = memory_service.create_memory(
            db=db,
            user_id=user_id,
            memory_type=payload.memory_type,
            content=payload.content,
            importance=payload.importance,
            confidence=payload.confidence,
            metadata=payload.metadata,
        )
        return memory
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to create memory for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create memory.",
        )


@router.post("/search", response_model=MemorySearchResponse)
@limiter.limit(settings.RATE_LIMIT_SEARCH)
def search_memories(
    request: Request,
    payload: MemorySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemorySearchResponse:
    """Semantic vector search across active memories for authenticated user with rate limiting."""
    user_id = current_user.id

    try:
        raw_results = memory_service.search_memories(
            db=db,
            user_id=user_id,
            query=payload.query,
            limit=payload.limit,
            min_similarity=payload.min_similarity,
        )

        results = [
            MemorySearchResult(
                id=str(r["id"]),
                content=r["content"],
                memory_type=r["memory_type"],
                importance=r["importance"],
                confidence=r["confidence"],
                similarity=r["similarity"],
            )
            for r in raw_results
        ]

        return MemorySearchResponse(
            results=results,
            query=payload.query,
            total=len(results),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to search memories for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search memories.",
        )


@router.get("/export", response_model=MemoryExportResponse)
def export_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryExportResponse:
    """Export all active memories for authenticated user."""
    user_id = current_user.id

    memories = memory_service.list_memories(
        db=db,
        user_id=user_id,
        is_active=True,
        limit=10_000,
    )

    return MemoryExportResponse(
        user_id=user_id,
        total_memories=len(memories),
        memories=memories,
        exported_at=datetime.now(timezone.utc),
    )


@router.delete("/all")
def delete_all_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete all memories for authenticated user (privacy/GDPR right to be forgotten)."""
    user_id = current_user.id

    try:
        deleted_count = memory_service.delete_all_user_memories(db=db, user_id=user_id)
        return {
            "deleted": deleted_count,
            "message": f"Successfully deleted {deleted_count} memories for user.",
        }
    except Exception as exc:
        logger.exception("Failed to delete all memories for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete all memories.",
        )


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 12 Phase 3: Ingestion & Job Management Endpoints
# (Registered prior to /{memory_id} to prevent path parameter collision)
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/ingest/file", response_model=MemoryArtifactJobResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.RATE_LIMIT_INGEST)
async def ingest_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Personal artifact file to ingest"),
    artifact_type: ArtifactType = Form(..., description="Artifact category"),
    context_notes: str | None = Form(default=None, description="Optional user contextual notes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryArtifactJobResponse:
    """
    Ingest a personal artifact file (PDF, text, letter, photo, audio transcript).
    Enforces MIME/signature verification, size limits, SHA-256 idempotency, and background processing.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    try:
        content = await file.read()
    except Exception as exc:
        logger.exception("Failed reading uploaded file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed reading uploaded file content.",
        )

    mime_type = file.content_type or "application/octet-stream"

    try:
        artifact, is_new = job_worker.handle_idempotent_upload(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            content=content,
            mime_type=mime_type,
            artifact_type=artifact_type,
            context_notes=context_notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to store artifact file for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store uploaded artifact.",
        )

    if is_new:
        job_worker.enqueue_job(
            artifact_id=artifact.id,
            background_tasks=background_tasks,
            context_notes=context_notes,
        )
        msg = "Artifact uploaded successfully. Processing enqueued in background."
    else:
        msg = f"Artifact already received (current status: {artifact.status})."

    return MemoryArtifactJobResponse(
        job_id=artifact.id,
        status=artifact.status,
        artifact_type=artifact.artifact_type,
        filename=artifact.filename,
        file_size_bytes=artifact.file_size_bytes,
        checksum_sha256=artifact.checksum_sha256,
        retry_count=artifact.retry_count,
        created_at=artifact.created_at,
        message=msg,
    )


@router.post("/ingest/text", response_model=MemoryArtifactJobResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.RATE_LIMIT_INGEST)
def ingest_text(
    request: Request,
    payload: TextIngestRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryArtifactJobResponse:
    """
    Ingest a plain-text note, letter, or reflection directly as a personal artifact.
    Enforces per-user idempotency and enqueues background memory extraction.
    """
    content_bytes = payload.content.encode("utf-8")
    filename = f"{payload.title.strip()}.txt"

    try:
        artifact, is_new = job_worker.handle_idempotent_upload(
            db=db,
            user_id=current_user.id,
            filename=filename,
            content=content_bytes,
            mime_type="text/plain",
            artifact_type=payload.artifact_type,
            context_notes=payload.context_notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to store text artifact for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store text artifact.",
        )

    if is_new:
        job_worker.enqueue_job(
            artifact_id=artifact.id,
            background_tasks=background_tasks,
            context_notes=payload.context_notes,
        )
        msg = "Text artifact received. Processing enqueued in background."
    else:
        msg = f"Text artifact already exists (status: {artifact.status})."

    return MemoryArtifactJobResponse(
        job_id=artifact.id,
        status=artifact.status,
        artifact_type=artifact.artifact_type,
        filename=artifact.filename,
        file_size_bytes=artifact.file_size_bytes,
        checksum_sha256=artifact.checksum_sha256,
        retry_count=artifact.retry_count,
        created_at=artifact.created_at,
        message=msg,
    )


@router.get("/ingest/{job_id}", response_model=MemoryArtifactJobDetailResponse)
def get_ingest_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryArtifactJobDetailResponse:
    """
    Poll status of an asynchronous memory ingestion job.
    Enforces strict user ownership isolation.
    """
    stmt = select(MemoryArtifact).where(
        MemoryArtifact.id == job_id,
        MemoryArtifact.user_id == current_user.id,
    )
    artifact = db.execute(stmt).scalar_one_or_none()
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion job not found.",
        )

    # Resolve extracted memory IDs linked to this artifact
    source_stmt = select(MemorySource.memory_id).where(
        MemorySource.artifact_id == artifact.id
    ).distinct()
    extracted_ids = list(db.scalars(source_stmt).all())

    return MemoryArtifactJobDetailResponse(
        job_id=artifact.id,
        user_id=artifact.user_id,
        status=artifact.status,
        artifact_type=artifact.artifact_type,
        filename=artifact.filename,
        file_size_bytes=artifact.file_size_bytes,
        checksum_sha256=artifact.checksum_sha256,
        retry_count=artifact.retry_count,
        error_message=artifact.error_message,
        context_notes=artifact.context_notes,
        created_at=artifact.created_at,
        processed_at=artifact.processed_at,
        extracted_memories_count=len(extracted_ids),
        extracted_memory_ids=extracted_ids,
    )


@router.get("/timeline", response_model=MemoryTimelineResponse)
def get_memory_timeline(
    start_date: date | None = Query(default=None, description="Filter memories on or after this event date"),
    end_date: date | None = Query(default=None, description="Filter memories on or before this event date"),
    precision: str | None = Query(default=None, description="Filter by event date precision: day, month, year, decade, unknown"),
    include_unknown_dates: bool = Query(default=True, description="Include memories without an explicit event date"),
    include_superseded: bool = Query(default=False, description="Include superseded historical memories"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Sort order by event date"),
    limit: int = Query(default=50, ge=1, le=100, description="Max memories to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryTimelineResponse:
    """
    Retrieve chronological memory timeline for authenticated user.
    Respects temporal precision, filtering, pagination, and user isolation.
    """
    try:
        items, total = memory_service.get_memory_timeline(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            precision=precision,
            include_unknown_dates=include_unknown_dates,
            include_superseded=include_superseded,
            order=order,
            limit=limit,
            offset=offset,
        )
        return MemoryTimelineResponse(
            items=[MemoryTimelineItem(**item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        logger.exception("Failed to retrieve memory timeline for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory timeline.",
        )


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryResponse:
    """Retrieve a specific memory by ID. Enforces ownership."""
    memory = memory_service.get_memory(db=db, user_id=current_user.id, memory_id=memory_id)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found.",
        )
    return memory


@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: UUID,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryResponse:
    """Update fields of an existing memory. Enforces ownership."""
    user_id = current_user.id

    try:
        memory = memory_service.update_memory(
            db=db,
            user_id=user_id,
            memory_id=memory_id,
            content=payload.content,
            importance=payload.importance,
            confidence=payload.confidence,
            is_active=payload.is_active,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to update memory %s: %s", memory_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update memory.",
        )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found.",
        )
    return memory


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Hard delete a memory by ID. Enforces ownership."""
    try:
        deleted = memory_service.delete_memory(db=db, user_id=current_user.id, memory_id=memory_id)
    except Exception as exc:
        logger.exception("Failed to delete memory %s: %s", memory_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete memory.",
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found.",
        )
    return {"deleted": True}


@router.post("/{memory_id}/deactivate")
def deactivate_memory(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Soft delete (deactivate) a memory by setting is_active=False. Enforces ownership."""
    try:
        deactivated = memory_service.deactivate_memory(
            db=db,
            user_id=current_user.id,
            memory_id=memory_id,
        )
    except Exception as exc:
        logger.exception("Failed to deactivate memory %s: %s", memory_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate memory.",
        )

    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found.",
        )
    return {"deactivated": True}


@router.get("/{memory_id}/provenance", response_model=MemoryProvenanceResponse)
def get_memory_provenance(
    memory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryProvenanceResponse:
    """
    Retrieve complete source provenance, artifact references, excerpts, and version history.
    Enforces strict user ownership isolation.
    """
    prov_data = memory_service.get_memory_provenance(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )
    if not prov_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found.",
        )
    return MemoryProvenanceResponse(**prov_data)


@router.post("/{memory_id}/correct", response_model=MemoryCorrectionResponse)
def correct_memory(
    memory_id: UUID,
    payload: MemoryCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryCorrectionResponse:
    """
    User-directed memory correction with concurrency-safe atomic supersession.
    Creates a new memory version, marks old version superseded, and preserves audit trail.
    """
    try:
        old_mem, new_mem = memory_service.correct_memory(
            db=db,
            user_id=current_user.id,
            memory_id=memory_id,
            content=payload.content,
            reason=payload.reason,
            memory_type=payload.memory_type,
            importance=payload.importance,
            confidence=payload.confidence,
            event_date=payload.event_date,
            event_date_precision=payload.event_date_precision,
        )
        return MemoryCorrectionResponse(
            success=True,
            old_memory=MemoryResponse.model_validate(old_mem),
            new_memory=MemoryResponse.model_validate(new_mem),
            correction_reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Failed to execute correction for memory %s: %s", memory_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to correct memory.",
        )

