"""HER AI — Ingestion Job Worker & Stale Job Watchdog.

Handles:
  - Background asynchronous task dispatching.
  - Per-user SHA-256 upload idempotency.
  - Watchdog recovery for interrupted/stuck processing jobs.
  - Retry policy with max attempt limits.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.artifact_security import (
    calculate_sha256,
    delete_artifact_file,
    save_artifact_file,
    validate_artifact_content,
)
from app.core.database import SessionLocal
from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.pipeline import memory_ingestion_pipeline

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
PROCESSING_TIMEOUT_SECONDS = 900  # 15 minutes


class BaseJobWorker(ABC):
    """Abstract interface for ingestion job queueing and watchdog recovery."""

    @abstractmethod
    def enqueue_job(
        self,
        artifact_id: UUID,
        background_tasks: BackgroundTasks,
        context_notes: str | None = None,
    ) -> None:
        """Enqueue an artifact for asynchronous processing."""
        pass

    @abstractmethod
    def recover_stuck_jobs(self, db: Session, timeout_seconds: int = PROCESSING_TIMEOUT_SECONDS) -> int:
        """Find and recover jobs stuck in 'processing' state past watchdog timeout."""
        pass


class BackgroundTaskWorker(BaseJobWorker):
    """FastAPI BackgroundTasks implementation of BaseJobWorker."""

    def enqueue_job(
        self,
        artifact_id: UUID,
        background_tasks: BackgroundTasks,
        context_notes: str | None = None,
    ) -> None:
        background_tasks.add_task(self._run_job_task, artifact_id, context_notes)

    def _run_job_task(self, artifact_id: UUID, context_notes: str | None = None) -> None:
        """Worker task executed asynchronously with an isolated DB session."""
        db = SessionLocal()
        try:
            artifact = db.get(MemoryArtifact, artifact_id)
            if not artifact:
                logger.error("Worker: Artifact %s not found.", artifact_id)
                return

            if artifact.status == "completed":
                logger.info("Worker: Artifact %s already completed.", artifact_id)
                return

            # Update status to processing with timestamp
            artifact.status = "processing"
            artifact.processing_started_at = datetime.now(timezone.utc)
            artifact.error_message = None
            db.commit()

            notes = context_notes or artifact.context_notes

            # Run processing through pipeline synchronously in this background worker thread
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                # Already in running loop
                task = asyncio.ensure_future(
                    memory_ingestion_pipeline.process_artifact(
                        db=db,
                        artifact_id=artifact_id,
                        context_notes=notes,
                    )
                )
                loop.run_until_complete(task)
            else:
                loop.run_until_complete(
                    memory_ingestion_pipeline.process_artifact(
                        db=db,
                        artifact_id=artifact_id,
                        context_notes=notes,
                    )
                )

            logger.info("Worker: Successfully processed artifact %s", artifact_id)

        except Exception as exc:
            db.rollback()
            logger.exception("Worker: Failed processing artifact %s: %s", artifact_id, exc)
            try:
                failed_artifact = db.get(MemoryArtifact, artifact_id)
                if failed_artifact:
                    failed_artifact.status = "failed"
                    failed_artifact.error_message = str(exc)
                    failed_artifact.processed_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                logger.exception("Worker: Could not update failed status for artifact %s", artifact_id)
        finally:
            db.close()

    def recover_stuck_jobs(self, db: Session, timeout_seconds: int = PROCESSING_TIMEOUT_SECONDS) -> int:
        """Find and recover stuck jobs."""
        threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
        stmt = select(MemoryArtifact).where(
            MemoryArtifact.status == "processing",
            MemoryArtifact.processing_started_at < threshold,
        )
        stuck_artifacts = db.scalars(stmt).all()
        recovered_count = 0

        for art in stuck_artifacts:
            art.retry_count += 1
            if art.retry_count > MAX_RETRIES:
                art.status = "failed"
                art.error_message = f"Job timed out after exceeding max retries ({MAX_RETRIES})."
                art.processed_at = datetime.now(timezone.utc)
            else:
                art.status = "pending"
                art.error_message = f"Recovered from stalled processing (attempt {art.retry_count}/{MAX_RETRIES})."
                art.processing_started_at = None

            recovered_count += 1

        if recovered_count > 0:
            db.commit()
            logger.warning("Watchdog recovered %d stuck jobs.", recovered_count)

        return recovered_count

    def handle_idempotent_upload(
        self,
        db: Session,
        user_id: UUID,
        filename: str,
        content: bytes,
        mime_type: str,
        artifact_type: str,
        context_notes: str | None = None,
    ) -> tuple[MemoryArtifact, bool]:
        """
        Idempotent upload handler:
        - Calculates SHA-256.
        - Checks for existing artifact with (user_id, checksum_sha256).
        - If completed: returns existing artifact, is_new=False.
        - If processing or pending: returns existing artifact, is_new=False.
        - If failed: allows retry by resetting to pending, is_new=True (needs enqueuing).
        - If not found: saves file securely and creates new MemoryArtifact, is_new=True.
        """
        validate_artifact_content(content, mime_type)
        checksum = calculate_sha256(content)

        stmt = select(MemoryArtifact).where(
            MemoryArtifact.user_id == user_id,
            MemoryArtifact.checksum_sha256 == checksum,
        ).order_by(MemoryArtifact.created_at.desc())

        existing = db.scalars(stmt).first()
        if existing:
            if existing.status in ("completed", "processing"):
                return existing, False
            if existing.status == "pending":
                return existing, False
            if existing.status == "failed":
                # Safe retry
                existing.status = "pending"
                existing.retry_count += 1
                existing.error_message = None
                existing.context_notes = context_notes or existing.context_notes
                db.commit()
                db.refresh(existing)
                return existing, True

        # New artifact
        storage_path, _, size_bytes = save_artifact_file(
            user_id=user_id,
            filename=filename,
            content=content,
            mime_type=mime_type,
        )

        new_artifact = MemoryArtifact(
            user_id=user_id,
            artifact_type=artifact_type,
            filename=filename,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=size_bytes,
            checksum_sha256=checksum,
            status="pending",
            context_notes=context_notes,
            retry_count=0,
        )
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)
        return new_artifact, True


job_worker = BackgroundTaskWorker()
