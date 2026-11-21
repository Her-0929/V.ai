"""HER AI — Milestone 12 Phase 1: Memory Foundation & Database Evolution Tests.

Tests:
  - Temporal date normalization & precision handling (day, month, year, decade, unknown).
  - Artifact security (MIME validation, magic byte verification, SHA-256, path traversal protection).
  - Database schema & model persistence for MemoryArtifact, Memory, and MemorySource.
  - Foreign key cascading and user ownership isolation.
  - Memory supersession integrity (validation, cross-user block, self-supersede block, cycle prevention).
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.artifact_security import (
    calculate_sha256,
    delete_artifact_file,
    sanitize_filename,
    save_artifact_file,
    validate_artifact_content,
)
from app.core.database import SessionLocal
from app.core.temporal import normalize_event_date
from app.models.memory import Memory
from app.models.memory_artifact import MemoryArtifact
from app.models.memory_source import MemorySource
from app.models.user import User
from app.services.memory_service import memory_service


# ──────────────────────────────────────────────────────────────────────────────
# 1. Temporal Grounding & Normalization Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_temporal_normalization_iso_day():
    d, prec = normalize_event_date("2023-04-12")
    assert d == date(2023, 4, 12)
    assert prec == "day"


def test_temporal_normalization_month():
    d, prec = normalize_event_date("2021-08")
    assert d == date(2021, 8, 1)
    assert prec == "month"


def test_temporal_normalization_year():
    d, prec = normalize_event_date("2019")
    assert d == date(2019, 1, 1)
    assert prec == "year"


def test_temporal_normalization_decade():
    d, prec = normalize_event_date("2010s")
    assert d == date(2010, 1, 1)
    assert prec == "decade"


def test_temporal_normalization_unknown_and_none():
    d1, prec1 = normalize_event_date(None)
    assert d1 is None
    assert prec1 == "unknown"

    d2, prec2 = normalize_event_date("unknown")
    assert d2 is None
    assert prec2 == "unknown"

    d3, prec3 = normalize_event_date("not-a-valid-date")
    assert d3 is None
    assert prec3 == "unknown"


# ──────────────────────────────────────────────────────────────────────────────
# 2. Artifact Security & Signature Validation Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_artifact_security_valid_pdf_magic_bytes():
    pdf_bytes = b"%PDF-1.4 sample content for document"
    # Should not raise
    validate_artifact_content(pdf_bytes, "application/pdf")
    sha = calculate_sha256(pdf_bytes)
    assert len(sha) == 64


def test_artifact_security_spoofed_mime_type_rejected():
    # PNG bytes labeled as PDF
    fake_pdf = b"\x89PNG\r\n\x1a\nNotAPdf"
    with pytest.raises(ValueError, match="magic signature"):
        validate_artifact_content(fake_pdf, "application/pdf")


def test_artifact_security_empty_content_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_artifact_content(b"", "text/plain")


def test_artifact_security_oversized_rejected():
    with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
        validate_artifact_content(b"A" * 100, "text/plain", max_size_bytes=50)


def test_artifact_security_filename_sanitization():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename(".hidden_file.txt") == "file_.hidden_file.txt"
    assert sanitize_filename("my letter (mom) [2020].pdf") == "my_letter__mom___2020_.pdf"


def test_artifact_save_and_delete_lifecycle(tmp_path, monkeypatch):
    test_user_id = uuid4()
    monkeypatch.setattr("app.core.config.settings.ARTIFACT_STORAGE_DIR", str(tmp_path))

    content = b"%PDF-1.4 valid test file"
    storage_path, checksum, size = save_artifact_file(
        user_id=test_user_id,
        filename="test_doc.pdf",
        content=content,
        mime_type="application/pdf",
    )

    assert os.path.exists(storage_path)
    assert size == len(content)
    assert len(checksum) == 64

    # Delete
    deleted = delete_artifact_file(storage_path)
    assert deleted is True
    assert not os.path.exists(storage_path)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Database Persistence & Foreign Key Constraints (Live PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_user(db_session):
    u = User(
        username=f"phase1_user_{uuid4().hex[:8]}",
        email=f"phase1_{uuid4().hex[:8]}@her.ai",
        is_active=True,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def test_memory_artifact_db_lifecycle(db_session, test_user):
    artifact = MemoryArtifact(
        user_id=test_user.id,
        artifact_type="document",
        filename="contract_2024.pdf",
        storage_path="/secure/storage/contract_2024.pdf",
        mime_type="application/pdf",
        file_size_bytes=1048576,
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="completed",
    )
    db_session.add(artifact)
    db_session.commit()
    db_session.refresh(artifact)

    assert artifact.id is not None
    assert artifact.user_id == test_user.id
    assert artifact.status == "completed"

    # Verify User.artifacts relationship
    db_session.refresh(test_user)
    assert artifact in test_user.artifacts


def test_memory_temporal_columns_persistence(db_session, test_user):
    event_d = date(2020, 6, 15)
    mem = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="life_event",
        content="Graduated from college with honors",
        importance=5,
        confidence=0.98,
        event_date=event_d,
        event_date_precision="day",
        source_created_at=datetime(2020, 6, 20, 10, 0, tzinfo=timezone.utc),
    )

    assert mem.event_date == event_d
    assert mem.event_date_precision == "day"
    assert mem.status == "active"
    assert mem.version == 1
    assert mem.superseded_by_id is None


def test_memory_source_artifact_linking(db_session, test_user):
    artifact = MemoryArtifact(
        user_id=test_user.id,
        artifact_type="letter",
        filename="letter_summer_2019.txt",
        storage_path="/secure/storage/letter_summer_2019.txt",
        mime_type="text/plain",
        file_size_bytes=512,
        checksum_sha256="abc1234298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="completed",
    )
    db_session.add(artifact)
    db_session.commit()
    db_session.refresh(artifact)

    mem = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="emotional_experience",
        content="Felt deeply nostalgic reading an old family letter",
        importance=4,
        confidence=0.9,
        artifact_id=artifact.id,
        source_type="letter",
        source_location="Page 1, Paragraph 2",
        source_metadata={"original_author": "Mother"},
    )

    db_session.refresh(mem)
    assert len(mem.sources) == 1
    source = mem.sources[0]
    assert source.source_type == "letter"
    assert source.artifact_id == artifact.id
    assert source.source_location == "Page 1, Paragraph 2"
    assert source.source_metadata["original_author"] == "Mother"


# ──────────────────────────────────────────────────────────────────────────────
# 4. Memory Supersession & Cycle Prevention Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_memory_supersession_success(db_session, test_user):
    old_mem = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="career_goal",
        content="User wants to work in game development",
        importance=3,
        confidence=0.8,
    )

    new_mem = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="career_goal",
        content="User decided to transition to AI systems research",
        importance=5,
        confidence=0.95,
    )

    updated_old = memory_service.supersede_memory(
        db=db_session,
        user_id=test_user.id,
        old_memory_id=old_mem.id,
        new_memory_id=new_mem.id,
        reason="Career direction change",
    )

    db_session.refresh(old_mem)
    db_session.refresh(new_mem)

    assert updated_old.status == "superseded"
    assert updated_old.superseded_by_id == new_mem.id
    assert updated_old.is_active is False
    assert new_mem.version == 2
    assert new_mem.memory_metadata["supersedes_memory_id"] == str(old_mem.id)


def test_memory_supersession_self_blocked(db_session, test_user):
    mem = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="general",
        content="Self reference test fact",
    )

    with pytest.raises(ValueError, match="cannot supersede itself"):
        memory_service.supersede_memory(
            db=db_session,
            user_id=test_user.id,
            old_memory_id=mem.id,
            new_memory_id=mem.id,
        )


def test_memory_supersession_cross_user_blocked(db_session, test_user):
    user_b = User(
        username=f"cross_user_{uuid4().hex[:8]}",
        email=f"cross_{uuid4().hex[:8]}@her.ai",
        is_active=True,
    )
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_b)

    mem_a = memory_service.create_memory(
        db=db_session,
        user_id=test_user.id,
        memory_type="personal_info",
        content="User A private detail",
    )

    mem_b = memory_service.create_memory(
        db=db_session,
        user_id=user_b.id,
        memory_type="personal_info",
        content="User B private detail",
    )

    # Attempting to supersede across users should fail with access/not found error
    with pytest.raises(ValueError, match="not found for user"):
        memory_service.supersede_memory(
            db=db_session,
            user_id=test_user.id,
            old_memory_id=mem_a.id,
            new_memory_id=mem_b.id,
        )


def test_memory_supersession_cycle_prevented(db_session, test_user):
    mem1 = memory_service.create_memory(
        db=db_session, user_id=test_user.id, memory_type="interest", content="Fact 1"
    )
    mem2 = memory_service.create_memory(
        db=db_session, user_id=test_user.id, memory_type="interest", content="Fact 2"
    )
    mem3 = memory_service.create_memory(
        db=db_session, user_id=test_user.id, memory_type="interest", content="Fact 3"
    )

    # Chain: mem1 -> superseded by mem2 -> superseded by mem3
    memory_service.supersede_memory(db_session, test_user.id, mem1.id, mem2.id)
    memory_service.supersede_memory(db_session, test_user.id, mem2.id, mem3.id)

    # Now attempt to make mem3 superseded by mem1 (cycle: mem1 -> mem2 -> mem3 -> mem1)
    with pytest.raises(ValueError, match="Supersession cycle detected"):
        memory_service.supersede_memory(db_session, test_user.id, mem3.id, mem1.id)

