"""HER AI — Verification & Retrieval Test Suite for HER_DAY Dataset Ingestion

Tests:
1. Target Retrieval Queries (6 canonical evaluation queries):
   - Query 1: "When did Vivek first see her?"
   - Query 2: "When did he find her social media ID?"
   - Query 3: "When did he confess his feelings?"
   - Query 4: "What happened on 12 June 2024?"
   - Query 5: "What does Vivek remember about their temple trips?"
   - Query 6: "What was the significance of 9 April 2025?"
2. Provenance & Artifact Traceability
3. Temporal Precision & Date Invariants
4. Ethical Boundaries & Synthetic Media Tagging
5. Chronological Timeline API Retrieval
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.memory import Memory
from app.models.memory_artifact import MemoryArtifact
from app.models.memory_source import MemorySource
from app.models.user import User
from app.services.memory_retrieval_service import memory_retrieval_service
from app.services.memory_service import memory_service


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def vivek_user(db_session):
    user = db_session.query(User).filter(User.username == "vivek").first()
    assert user is not None, "User 'vivek' must exist in the database (run ingest_her_day_dataset.py first)"
    return user


class TestHerDayDatasetIntegrity:
    """Verify that all dataset records are persisted with full fidelity."""

    def test_artifact_registered(self, db_session, vivek_user):
        artifact = db_session.query(MemoryArtifact).filter(
            MemoryArtifact.user_id == vivek_user.id,
            MemoryArtifact.filename == "HER_AI_HER_DAY_dataset_v1.zip",
        ).first()
        assert artifact is not None
        assert artifact.status == "completed"
        assert artifact.checksum_sha256 is not None
        assert "ethical_rules" in artifact.context_notes

    def test_memory_counts(self, db_session, vivek_user):
        memories = db_session.query(Memory).filter(
            Memory.user_id == vivek_user.id,
            Memory.is_active.is_(True),
        ).all()
        # 8 structured memories + 12 timeline events + 11 narrative chunks = 31 total
        assert len(memories) >= 31, f"Expected at least 31 memories, found {len(memories)}"

        sources = db_session.query(MemorySource).join(Memory).filter(
            Memory.user_id == vivek_user.id
        ).all()
        assert len(sources) >= 28, f"Expected at least 28 source links, found {len(sources)}"

    def test_ethical_boundaries_and_synthetic_flags(self, db_session, vivek_user):
        # Friendship boundary
        boundary_mem = db_session.query(Memory).filter(
            Memory.user_id == vivek_user.id,
            Memory.content.ilike("%just friends%"),
        ).first()
        assert boundary_mem is not None
        assert boundary_mem.memory_metadata.get("boundary_enforced") is True

        # AI-generated images
        synthetic_mem = db_session.query(Memory).filter(
            Memory.user_id == vivek_user.id,
            Memory.content.ilike("%AI-generated%"),
        ).first()
        assert synthetic_mem is not None
        assert "synthetic" in synthetic_mem.content.lower() or synthetic_mem.memory_metadata.get("is_synthetic_content") is True


class TestHerDayTargetRetrieval:
    """Verify vector retrieval on the 6 canonical evaluation queries."""

    def test_query_1_first_sighting(self, db_session, vivek_user):
        """Query 1: When did Vivek first see her?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="When did Vivek first see her?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        # Should match the first sighting memory (14 April 2017 / boarding bus)
        combined_text = " ".join([r["content"] for r in results[:2]])
        assert "2017" in combined_text or "14" in combined_text
        assert "bus" in combined_text.lower() or "first" in combined_text.lower()
        assert top["similarity"] >= 0.50

    def test_query_2_social_media_id(self, db_session, vivek_user):
        """Query 2: When did he find her social media ID?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="When did he find her social media ID?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        combined_text = " ".join([r["content"] for r in results[:2]])
        assert "2023-08-08" in combined_text or "8 August 2023" in combined_text or "August 2023" in combined_text
        assert "social media" in combined_text.lower() or "id" in combined_text.lower()
        assert top["similarity"] >= 0.50

    def test_query_3_confession(self, db_session, vivek_user):
        """Query 3: When did he confess his feelings?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="When did he confess his feelings?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        combined_text = " ".join([r["content"] for r in results[:2]])
        assert "2023-08-12" in combined_text or "12 August 2023" in combined_text or "confess" in combined_text.lower()
        assert top["similarity"] >= 0.50

    def test_query_4_first_conversation_and_boundary(self, db_session, vivek_user):
        """Query 4: What happened on 12 June 2024?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="What happened on 12 June 2024?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        combined_text = " ".join([r["content"] for r in results[:2]])
        # Must include the friendship boundary
        assert "friend" in combined_text.lower() or "talked to me" in combined_text.lower()
        assert top["similarity"] >= 0.10

    def test_query_5_temple_trips(self, db_session, vivek_user):
        """Query 5: What does Vivek remember about their temple trips?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="What does Vivek remember about their temple trips?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        assert "temple" in top["content"].lower()
        assert top["similarity"] >= 0.40

    def test_query_6_april_9_2025(self, db_session, vivek_user):
        """Query 6: What was the significance of 9 April 2025?"""
        results = memory_retrieval_service.search_similar_memories(
            db=db_session,
            user_id=vivek_user.id,
            query="What was the significance of 9 April 2025?",
            limit=3,
        )
        assert len(results) > 0
        top = results[0]
        combined_text = " ".join([r["content"] for r in results[:2]])
        assert "beautiful" in combined_text.lower() or "treasure" in combined_text.lower() or "gift" in combined_text.lower() or "2025-04-09" in combined_text
        assert top["similarity"] >= 0.20


class TestHerDayTimelineAndProvenance:
    """Verify chronological timeline retrieval and source provenance."""

    def test_timeline_chronological_ordering(self, db_session, vivek_user):
        items, total = memory_service.get_memory_timeline(
            db=db_session,
            user_id=vivek_user.id,
            order="asc",
            limit=50,
            include_unknown_dates=False,
        )
        assert total >= 13  # At least 12 timeline events + first sighting structured memory with date
        dates = [item["event_date"] for item in items if item["event_date"]]
        # Verify monotonically ascending order
        assert dates == sorted(dates)

    def test_timeline_precision_formatting(self, db_session, vivek_user):
        items, total = memory_service.get_memory_timeline(
            db=db_session,
            user_id=vivek_user.id,
            precision="day",
            limit=50,
        )
        assert total > 0
        for item in items:
            assert item["event_date_precision"] == "day"
            assert item["formatted_date"] is not None

    def test_provenance_traceability(self, db_session, vivek_user):
        # Pick any memory with sources
        mem = db_session.query(Memory).filter(
            Memory.user_id == vivek_user.id,
            Memory.sources.any(),
        ).first()
        assert mem is not None
        assert len(mem.sources) > 0
        src = mem.sources[0]
        assert src.artifact_id is not None
        assert src.source_reference.startswith("http")
        assert src.source_location is not None
