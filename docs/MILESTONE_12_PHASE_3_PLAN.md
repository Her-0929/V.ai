# HER AI — Milestone 12 Phase 3: Architecture Plan & Implementation Specifications
## Personal Memory Intelligence — REST APIs, Job Management & RAG Integration

> **Document Version:** 2.0.0 (Approved with Mandatory Engineering Improvements)  
> **Date:** 2026-11-17  
> **Target Release:** HER AI v0.4.0  
> **Status:** Approved for Implementation  
> **Baseline:** 122/122 automated tests passing; Alembic revision head `c3d4e5f6a7b8`  

---

## 1. Executive Summary & Required Amendments

This specification incorporates the mandatory architectural amendments required for production-grade reliability, concurrency safety, and provenance integrity:

1. **Asynchronous Job Reliability:**
   - Persistent state tracking via `memory_artifacts` table.
   - Automatic recovery of interrupted/stuck processing jobs (configurable timeout, default 15 minutes).
   - `retry_count` tracking and maximum retry policy (`MAX_RETRIES = 3`).
   - Clean worker abstraction (`BaseJobWorker`, `BackgroundTaskWorker`) designed for straightforward future extraction to Celery/ARQ without requiring Redis now.
2. **Per-User Idempotency & Concurrency:**
   - Strict per-user SHA-256 deduplication protecting against concurrent duplicate uploads.
   - Multi-state idempotency:
     - `completed`: Return existing job and extracted memory references immediately.
     - `pending` / `processing`: Return existing active job status without re-queuing duplicate work.
     - `failed`: Allow safe retry by resetting state to `pending` and incrementing `retry_count`.
   - Complete cross-tenant file and job isolation.
3. **Transaction-Safe Memory Corrections:**
   - Row-level locking via SQLAlchemy `with_for_update()` to prevent concurrent conflicting corrections.
   - Safe embedding generation: generate embedding *before* acquiring the row lock to avoid holding DB transaction locks during embedding computation.
   - Atomic transaction: old-memory deactivation/supersession and new-memory creation committed in a single transaction.
   - Separate audit metadata (`correction_reason`, `superseded_at`, `corrected_by_user_id`) distinct from source excerpts.
4. **Precision-Aware Temporal Handling:**
   - Full support for `day`, `month`, `year`, `decade`, and `unknown` precisions.
   - Invariant: A year-level memory (e.g. "Graduated college in 2018") must never be presented as an exact date ("2018-01-01").
   - Timeline filtering and RAG prompts render precision explicitly (e.g., `"2018 (year)"` vs `"April 12, 2023 (exact day)"`).
5. **Provenance Integrity:**
   - Preserve original artifact references during memory correction.
   - Create explicit manual correction provenance while preserving original document sources.
   - Strict cross-user information leakage prevention (artifact metadata cannot be queried across tenants).
6. **Structured RAG Grounding:**
   - Inject structured memories with event date, precision, importance, confidence, source type, artifact filename, and source location.
   - Strictly filter `status == 'active'` (excluding superseded/disputed memories).
   - Invariant prompt instructions preventing prompt injection from retrieved personal data and prohibiting false claims of AI consciousness.
7. **Additive Alembic Migration:**
   - Add `context_notes: Text | None`, `retry_count: Integer`, `processing_started_at: DateTime | None` to `memory_artifacts`.
   - Add composite index on `(user_id, checksum_sha256)`.

---

## 2. Database Evolution & Schema Specifications

### 2.1 New Additive Migration: `d4e5f6a7b8c9_enhance_memory_artifacts_for_jobs.py`
```python
"""Enhance memory_artifacts for job recovery, retry, and context notes.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-17
"""
```

**Schema Additions to `memory_artifacts`:**
- `context_notes`: `Text`, nullable=True (Persists user-supplied notes across async jobs and server restarts).
- `retry_count`: `Integer`, default=0, nullable=False (Tracks automatic/manual retries).
- `processing_started_at`: `DateTime(timezone=True)`, nullable=True (Used for watchdog timeout detection of stuck jobs).
- Composite index: `ix_memory_artifacts_user_checksum` on `['user_id', 'checksum_sha256']`.

---

## 3. Worker Abstraction & Asynchronous Job Lifecycle

### 3.1 Worker Interface (`backend/app/services/ingestion/worker.py`)
```python
class BaseJobWorker(ABC):
    @abstractmethod
    async def enqueue_artifact_job(self, artifact_id: UUID, background_tasks: BackgroundTasks) -> None:
        """Enqueue an artifact for processing."""
        pass

    @abstractmethod
    def recover_stuck_jobs(self, db: Session, timeout_seconds: int = 900) -> int:
        """Find and recover jobs stuck in 'processing' state past timeout."""
        pass
```

### 3.2 Job Lifecycle & State Transitions
```text
           [Client Upload]
                 │
                 ▼
          ┌─────────────┐
          │   PENDING   │ ◄─── (Retry if failed & retry_count < MAX_RETRIES)
          └──────┬──────┘
                 │ Worker picks up job
                 ▼
          ┌─────────────┐
          │ PROCESSING  │ ───► Watchdog Timeout (>15m) ──► Re-queue / FAILED
          └──────┬──────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
 ┌─────────────┐   ┌─────────────┐
 │  COMPLETED  │   │   FAILED    │
 └─────────────┘   └─────────────┘
```

---

## 4. REST API Route Ordering & Endpoint Specifications

### 4.1 Strict Route Ordering in `app/api/memories.py`
1. `GET /api/memories` — List memories
2. `POST /api/memories` — Create memory
3. `POST /api/memories/search` — Vector search
4. `GET /api/memories/export` — Export memories
5. `DELETE /api/memories/all` — Purge memories
6. `POST /api/memories/ingest/file` — Multipart file ingestion
7. `POST /api/memories/ingest/text` — Direct note ingestion
8. `GET /api/memories/ingest/{job_id}` — Ingestion job status polling
9. `GET /api/memories/timeline` — Chronological memory retrieval
10. `GET /api/memories/{memory_id}` — Single memory lookup
11. `PATCH /api/memories/{memory_id}` — Memory field update
12. `DELETE /api/memories/{memory_id}` — Memory hard deletion
13. `POST /api/memories/{memory_id}/deactivate` — Soft deactivation
14. `GET /api/memories/{memory_id}/provenance` — Memory source audit
15. `POST /api/memories/{memory_id}/correct` — Transaction-safe correction

---

## 5. Staged Implementation Roadmap

- **Stage 1:** Additive Alembic Migration & Model Updates
- **Stage 2:** Asynchronous Worker Abstraction, Stuck Job Recovery & Idempotent Ingestion
- **Stage 3:** Schemas & REST Endpoints (`/ingest/file`, `/ingest/text`, `/ingest/{job_id}`)
- **Stage 4:** Concurrency-Safe Memory Correction & Provenance Endpoints (`/correct`, `/provenance`)
- **Stage 5:** Precision-Aware Temporal Timeline (`/timeline`) & RAG Context Enhancement
- **Stage 6:** Comprehensive Test Suite & Documentation Verification
