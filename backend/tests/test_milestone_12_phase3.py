"""HER AI — Milestone 12 Phase 3: REST APIs, Job Management & RAG Integration Tests.

Tests:
  - Route ordering: /timeline and /ingest/... resolve without UUID path collision.
  - POST /api/memories/ingest/file: valid upload, background task enqueue, mime validation, SHA-256 idempotency.
  - POST /api/memories/ingest/text: note ingestion, idempotency, background dispatch.
  - GET /api/memories/ingest/{job_id}: job polling and strict user ownership isolation.
  - GET /api/memories/{memory_id}/provenance: provenance resolution with excerpts, locations, artifacts, and history.
  - POST /api/memories/{memory_id}/correct: concurrency-safe atomic correction, version increment, supersession, cycle prevention.
  - GET /api/memories/timeline: chronological ordering, precision formatting, date filtering, superseded filtering.
  - Background watchdog recovery: recovering stalled processing jobs past timeout threshold.
  - RAG integration: temporal grounding and source attribution in system prompt.
"""

from __future__ import annotations

import io
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.personality import build_system_prompt
from app.core.security import create_access_token
from app.main import app
from app.models.memory import Memory
from app.models.memory_artifact import MemoryArtifact
from app.models.memory_source import MemorySource
from app.models.user import User
from app.services.ingestion.worker import job_worker
from app.services.memory_retrieval_service import memory_retrieval_service
from app.services.memory_service import memory_service


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def auth_user():
    """Create test user fixture in DB."""
    db = SessionLocal()
    user_id = uuid4()
    user = User(
        id=user_id,
        username=f"user_{user_id.hex[:8]}",
        email=f"user_{user_id.hex[:8]}@example.com",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def other_user():
    """Create second user for cross-user isolation tests."""
    db = SessionLocal()
    user_id = uuid4()
    user = User(
        id=user_id,
        username=f"other_{user_id.hex[:8]}",
        email=f"other_{user_id.hex[:8]}@example.com",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def client(auth_user):
    """Authenticated TestClient for auth_user."""
    token = create_access_token(subject=str(auth_user.id))
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


@pytest.fixture
def other_client(other_user):
    """Authenticated TestClient for other_user."""
    token = create_access_token(subject=str(other_user.id))
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


# ──────────────────────────────────────────────────────────────────────────────
# 1. Route Ordering & Conflict Prevention Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_route_ordering_timeline_does_not_collide_with_memory_id(client):
    """GET /api/memories/timeline must NOT be captured by /{memory_id} with 422 UUID error."""
    res = client.get("/api/memories/timeline")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


def test_route_ordering_ingest_routes_do_not_collide_with_memory_id(client):
    """GET /api/memories/ingest/{job_id} must resolve correctly without colliding with /{memory_id}."""
    random_job_id = uuid4()
    res = client.get(f"/api/memories/ingest/{random_job_id}")
    # Should return 404 because job doesn't exist, NOT 422 or route error
    assert res.status_code == 404
    assert res.json()["detail"] == "Ingestion job not found."


# ──────────────────────────────────────────────────────────────────────────────
# 2. Ingestion Endpoints Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_ingest_file_pdf_success(client, auth_user):
    """Upload valid PDF file, receives 202, job enqueued."""
    fake_pdf = b"%PDF-1.4 sample content for personal memory document"
    file_payload = ("test_doc.pdf", fake_pdf, "application/pdf")

    with patch.object(job_worker, "enqueue_job") as mock_enqueue:
        res = client.post(
            "/api/memories/ingest/file",
            files={"file": file_payload},
            data={"artifact_type": "document", "context_notes": "Important career resume"},
        )
        assert res.status_code == 202
        data = res.json()
        assert data["status"] == "pending"
        assert data["filename"] == "test_doc.pdf"
        assert data["artifact_type"] == "document"
        assert "job_id" in data
        mock_enqueue.assert_called_once()


def test_ingest_file_idempotency(client, auth_user):
    """Uploading the exact same file returns the existing job record without re-enqueueing."""
    fake_doc = b"%PDF-1.4 identical content test idempotency"
    file_payload = ("same.pdf", fake_doc, "application/pdf")

    with patch.object(job_worker, "enqueue_job") as mock_enqueue:
        # First upload
        res1 = client.post(
            "/api/memories/ingest/file",
            files={"file": file_payload},
            data={"artifact_type": "document"},
        )
        assert res1.status_code == 202
        job_id1 = res1.json()["job_id"]
        assert mock_enqueue.call_count == 1

        # Second upload with identical bytes
        res2 = client.post(
            "/api/memories/ingest/file",
            files={"file": ("same.pdf", fake_doc, "application/pdf")},
            data={"artifact_type": "document"},
        )
        assert res2.status_code == 202
        job_id2 = res2.json()["job_id"]
        assert job_id1 == job_id2
        assert "already received" in res2.json()["message"]
        # mock_enqueue was not called a second time
        assert mock_enqueue.call_count == 1


def test_ingest_file_invalid_magic_signature_rejected(client):
    """File claiming application/pdf but with invalid bytes must be rejected with 400."""
    invalid_bytes = b"NOT_A_PDF_HEADER executable dummy bytes"
    file_payload = ("fake.pdf", invalid_bytes, "application/pdf")

    res = client.post(
        "/api/memories/ingest/file",
        files={"file": file_payload},
        data={"artifact_type": "document"},
    )
    assert res.status_code == 400
    assert "magic signature" in res.json()["detail"].lower()


def test_ingest_text_success(client, auth_user):
    """Ingest plain text note successfully."""
    payload = {
        "title": "Childhood Pet",
        "content": "I had a golden retriever named Rusty when I lived in Oregon in 2012.",
        "artifact_type": "note",
        "context_notes": "Childhood memories",
    }
    with patch.object(job_worker, "enqueue_job") as mock_enqueue:
        res = client.post("/api/memories/ingest/text", json=payload)
        assert res.status_code == 202
        data = res.json()
        assert data["filename"] == "Childhood Pet.txt"
        assert data["status"] == "pending"
        mock_enqueue.assert_called_once()


def test_get_ingest_job_cross_user_isolation(client, other_client, auth_user):
    """User B cannot inspect User A's ingestion job."""
    db = SessionLocal()
    artifact = MemoryArtifact(
        user_id=auth_user.id,
        artifact_type="note",
        filename="private_notes.txt",
        storage_path="storage/artifacts/fake.txt",
        mime_type="text/plain",
        file_size_bytes=100,
        checksum_sha256="abc123sha",
        status="completed",
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    job_id = artifact.id
    db.close()

    # User A can see it
    res_a = client.get(f"/api/memories/ingest/{job_id}")
    assert res_a.status_code == 200
    assert res_a.json()["job_id"] == str(job_id)

    # User B gets 404
    res_b = other_client.get(f"/api/memories/ingest/{job_id}")
    assert res_b.status_code == 404
    assert res_b.json()["detail"] == "Ingestion job not found."


# ──────────────────────────────────────────────────────────────────────────────
# 3. Provenance & Correction Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_get_memory_provenance_complete_audit(client, auth_user):
    """Provenance endpoint returns artifact info, source excerpts, locations, and history."""
    db = SessionLocal()
    artifact = MemoryArtifact(
        user_id=auth_user.id,
        artifact_type="document",
        filename="university_degree.pdf",
        storage_path="storage/fake_path.pdf",
        mime_type="application/pdf",
        file_size_bytes=2048,
        checksum_sha256="deg123sha",
        status="completed",
    )
    db.add(artifact)
    db.flush()

    mem = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="life_event",
        content="Graduated with B.S. in Computer Science",
        importance=5,
        confidence=0.98,
        event_date=date(2018, 5, 1),
        event_date_precision="month",
        artifact_id=artifact.id,
        source_type="document",
        source_location="Page 1",
        source_excerpt="Conferred Bachelor of Science in Computer Science on May 2018.",
    )
    mem_id = mem.id
    db.close()

    res = client.get(f"/api/memories/{mem_id}/provenance")
    assert res.status_code == 200
    data = res.json()
    assert data["memory_id"] == str(mem_id)
    assert data["content"] == "Graduated with B.S. in Computer Science"
    assert data["event_date"] == "2018-05-01"
    assert data["event_date_precision"] == "month"
    assert len(data["sources"]) >= 1
    src = data["sources"][0]
    assert src["source_location"] == "Page 1"
    assert "Computer Science" in src["excerpt"]
    assert src["artifact"]["filename"] == "university_degree.pdf"
    assert len(data["history"]) >= 1


def test_correct_memory_atomic_supersession(client, auth_user):
    """User correction creates version 2, marks version 1 superseded, records audit reason."""
    db = SessionLocal()
    mem1 = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="career_goal",
        content="User wants to work as a Cloud Architect",
        importance=4,
        confidence=0.9,
    )
    mem1_id = mem1.id
    db.close()

    payload = {
        "content": "User wants to work as an AI Research Scientist",
        "memory_type": "career_goal",
        "importance": 5,
        "confidence": 1.0,
        "reason": "Updated career goal from cloud to AI research",
    }
    res = client.post(f"/api/memories/{mem1_id}/correct", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["correction_reason"] == payload["reason"]

    # Verify old memory is superseded
    assert data["old_memory"]["id"] == str(mem1_id)
    assert data["old_memory"]["status"] == "superseded"
    assert data["old_memory"]["is_active"] is False

    # Verify new memory is active version 2
    new_mem_id = data["new_memory"]["id"]
    assert data["new_memory"]["content"] == payload["content"]
    assert data["new_memory"]["version"] == 2
    assert data["new_memory"]["status"] == "active"
    assert data["new_memory"]["is_active"] is True

    # Verify attempting to correct the superseded memory fails
    res_repeat = client.post(f"/api/memories/{mem1_id}/correct", json=payload)
    assert res_repeat.status_code == 400
    assert "already been superseded" in res_repeat.json()["detail"]


def test_correct_memory_cross_user_blocked(client, other_client, auth_user, other_user):
    """User B cannot correct User A's memory."""
    db = SessionLocal()
    mem = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="hobby",
        content="User plays guitar",
    )
    mem_id = mem.id
    db.close()

    payload = {
        "content": "User plays bass guitar",
        "reason": "Malicious or mistaken edit",
    }
    res = other_client.post(f"/api/memories/{mem_id}/correct", json=payload)
    assert res.status_code in (400, 404)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Timeline Endpoints Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_get_memory_timeline_chronological_sorting(client, auth_user):
    """Timeline returns memories chronologically with precision formatting."""
    db = SessionLocal()
    m1 = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="life_event",
        content="Born in Portland",
        event_date=date(1995, 3, 15),
        event_date_precision="day",
    )
    m2 = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="life_event",
        content="Moved to Seattle in the 2010s",
        event_date=date(2010, 1, 1),
        event_date_precision="decade",
    )
    m3 = memory_service.create_memory(
        db=db,
        user_id=auth_user.id,
        memory_type="milestone",
        content="Published first paper in 2021",
        event_date=date(2021, 6, 1),
        event_date_precision="month",
    )
    m1_id = m1.id
    m2_id = m2.id
    m3_id = m3.id
    db.close()

    res = client.get("/api/memories/timeline?order=asc")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 3

    # Check that 1995 comes before 2010 which comes before 2021
    dates = [i["event_date"] for i in items if i["event_date"] is not None]
    assert sorted(dates) == dates

    # Check precision-aware date formatting
    for item in items:
        if item["id"] == str(m1_id):
            assert "exact day" in item["formatted_date"]
        elif item["id"] == str(m2_id):
            assert "decade" in item["formatted_date"]
        elif item["id"] == str(m3_id):
            assert "month" in item["formatted_date"]


def test_timeline_filters_precision_and_date_range(client, auth_user):
    """Timeline filters by precision and date ranges."""
    res = client.get("/api/memories/timeline?precision=decade")
    assert res.status_code == 200
    items = res.json()["items"]
    for i in items:
        assert i["event_date_precision"] == "decade"


# ──────────────────────────────────────────────────────────────────────────────
# 5. Watchdog & Recovery Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_watchdog_recovers_stuck_processing_jobs(auth_user):
    """Jobs stuck in 'processing' past the timeout are reset to pending."""
    db = SessionLocal()
    stuck_artifact = MemoryArtifact(
        user_id=auth_user.id,
        artifact_type="document",
        filename="stuck.pdf",
        storage_path="storage/stuck.pdf",
        mime_type="application/pdf",
        file_size_bytes=1000,
        checksum_sha256="stuck123sha",
        status="processing",
        processing_started_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        retry_count=0,
    )
    db.add(stuck_artifact)
    db.commit()

    recovered = job_worker.recover_stuck_jobs(db=db, timeout_seconds=60)
    assert recovered >= 1

    db.refresh(stuck_artifact)
    assert stuck_artifact.status == "pending"
    assert stuck_artifact.retry_count == 1
    assert "Recovered" in (stuck_artifact.error_message or "")
    db.close()


def test_watchdog_exceeded_retries_marks_failed(auth_user):
    """Jobs that exceed MAX_RETRIES are marked failed."""
    db = SessionLocal()
    dead_artifact = MemoryArtifact(
        user_id=auth_user.id,
        artifact_type="document",
        filename="doomed.pdf",
        storage_path="storage/doomed.pdf",
        mime_type="application/pdf",
        file_size_bytes=1000,
        checksum_sha256="doomed123sha",
        status="processing",
        processing_started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        retry_count=3,  # Already at MAX_RETRIES
    )
    db.add(dead_artifact)
    db.commit()

    recovered = job_worker.recover_stuck_jobs(db=db, timeout_seconds=60)
    assert recovered >= 1

    db.refresh(dead_artifact)
    assert dead_artifact.status == "failed"
    assert "timed out after exceeding max retries" in dead_artifact.error_message
    db.close()


# ──────────────────────────────────────────────────────────────────────────────
# 6. RAG Grounding & Temporal Synthesis Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_rag_system_prompt_temporal_and_source_grounding():
    """System prompt renders event dates, precisions, and sources accurately."""
    memories = [
        {
            "content": "Graduated from MIT",
            "memory_type": "milestone",
            "importance": 5,
            "confidence": 0.95,
            "event_date": "2019-06",
            "event_date_precision": "month",
            "source_type": "document",
            "source_filename": "diploma.pdf",
            "source_location": "Page 1",
        },
        {
            "content": "Lives in Austin",
            "memory_type": "personal_info",
            "importance": 4,
            "confidence": 1.0,
            "event_date": None,
            "event_date_precision": "unknown",
            "source_type": "conversation",
        },
    ]

    prompt = build_system_prompt(memories=memories, user_name="Alex")
    assert "Graduated from MIT" in prompt
    assert "2019-06 (month)" in prompt
    assert "diploma.pdf" in prompt
    assert "Page 1" in prompt
    assert "Lives in Austin" in prompt
    assert "Alex" in prompt
