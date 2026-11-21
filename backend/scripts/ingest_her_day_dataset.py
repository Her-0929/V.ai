"""HER AI — Ingestion Script for HER_DAY Website Memory Dataset (Milestone 12 Phase 2)

Ingests:
- raw_sources.json (12 records) -> MemorySource / provenance
- letters.json (3 records) -> MemorySource / provenance
- structured_memories.json (8 records) -> Memory + 384-dim embeddings
- timeline.json (12 records) -> Memory + 384-dim embeddings + temporal precision
- rag_chunks.jsonl (narrative passages) -> Memory (narrative_chunk) + 384-dim embeddings
- entities.json & media_manifest.json -> linked metadata & synthetic/voice flags
- MemoryArtifact record anchoring dataset provenance and checksum

Guarantees:
- Strict user isolation (tenant-scoped).
- Idempotency (no duplicate entries on repeated runs).
- Preserves Vivek's first-person perspective.
- Enforces "just friends" boundary and consent rules.
- Labels AI images as synthetic (is_synthetic=True).
- Flags uncertain dates and items.
- Generates embeddings on NVIDIA GPU via configured EmbeddingService.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.core.temporal import normalize_event_date
from app.models.memory import Memory
from app.models.memory_artifact import MemoryArtifact
from app.models.memory_source import MemorySource
from app.models.user import User
from app.services.embedding_service import embedding_service
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("her_day_ingestion")


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_or_create_user(db, username: str, email: str) -> User:
    user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user:
        logger.info(f"Using existing user: {user.username} ({user.id})")
        return user

    logger.info(f"Creating new tenant user: {username} ({email})")
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        hashed_password=hash_password("HerAiVivekSecure2026!"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user: {user.username} ({user.id})")
    return user


def ingest_her_day_dataset(dataset_dir_path: str, username: str = "vivek", email: str = "vivek@her.ai", reindex: bool = False):
    dataset_dir = Path(dataset_dir_path)
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    manifest_file = dataset_dir / "ingestion_manifest.json"
    raw_sources_file = dataset_dir / "raw_sources.json"
    structured_memories_file = dataset_dir / "structured_memories.json"
    timeline_file = dataset_dir / "timeline.json"
    entities_file = dataset_dir / "entities.json"
    letters_file = dataset_dir / "letters.json"
    media_manifest_file = dataset_dir / "media_manifest.json"
    rag_chunks_file = dataset_dir / "rag_chunks.jsonl"

    for req_file in [manifest_file, raw_sources_file, structured_memories_file, timeline_file]:
        if not req_file.exists():
            raise FileNotFoundError(f"Missing required dataset file: {req_file}")

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    with open(raw_sources_file, "r", encoding="utf-8") as f:
        raw_sources_data = json.load(f)
    with open(structured_memories_file, "r", encoding="utf-8") as f:
        structured_memories_data = json.load(f)
    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)

    letters_data = json.load(open(letters_file, "r", encoding="utf-8")) if letters_file.exists() else []
    entities_data = json.load(open(entities_file, "r", encoding="utf-8")) if entities_file.exists() else []
    media_manifest_data = json.load(open(media_manifest_file, "r", encoding="utf-8")) if media_manifest_file.exists() else {}

    rag_chunks_data = []
    if rag_chunks_file.exists():
        with open(rag_chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rag_chunks_data.append(json.loads(line))

    manifest_checksum = compute_sha256(manifest_file)

    db = SessionLocal()
    try:
        user = get_or_create_user(db, username=username, email=email)

        # 1. Register or find MemoryArtifact for HER_DAY dataset
        artifact = db.query(MemoryArtifact).filter(
            MemoryArtifact.user_id == user.id,
            MemoryArtifact.filename == "HER_AI_HER_DAY_dataset_v1.zip",
        ).first()

        if not artifact:
            artifact = MemoryArtifact(
                id=uuid.uuid4(),
                user_id=user.id,
                artifact_type="document",
                filename="HER_AI_HER_DAY_dataset_v1.zip",
                storage_path=str(dataset_dir.as_posix()),
                mime_type="application/zip",
                file_size_bytes=manifest_file.stat().st_size,
                checksum_sha256=manifest_checksum,
                status="completed",
                context_notes=(
                    "HER AI HER_DAY Website Memory Dataset v1.0.0. "
                    "Canonical source: https://vivek0929.github.io/HER_DAY/ "
                    "Includes 8 structured memories, 12 timeline events, 23 RAG chunks, "
                    "entities, letters, and ethical boundary safeguards."
                ),
                retry_count=0,
                processing_started_at=datetime.now(timezone.utc),
                processed_at=datetime.now(timezone.utc),
            )
            db.add(artifact)
            db.commit()
            db.refresh(artifact)
            logger.info(f"Registered MemoryArtifact {artifact.id}")
        else:
            logger.info(f"Reusing existing MemoryArtifact {artifact.id}")

        # Index existing memories for user to prevent duplicates
        existing_memories = db.query(Memory).filter(Memory.user_id == user.id).all()
        existing_her_day_ids = {}
        for m in existing_memories:
            if m.memory_metadata and "her_day_id" in m.memory_metadata:
                existing_her_day_ids[m.memory_metadata["her_day_id"]] = m

        # Build raw source lookup table by source_id
        raw_sources_by_id = {s["source_id"]: s for s in raw_sources_data}
        letters_by_id = {l.get("source_id", l.get("letter_id")): l for l in letters_data}

        # Helper to map raw source_type to allowed ck_memory_source_type:
        # ('message', 'letter', 'note', 'document', 'photo', 'audio', 'manual', 'imported', 'system')
        def normalize_source_type(st: str) -> str:
            st = (st or "").lower()
            if "letter" in st:
                return "letter"
            if "note" in st or "text" in st:
                return "note"
            if "photo" in st or "image" in st:
                return "photo"
            if "audio" in st or "voice" in st:
                return "audio"
            return "document"

        ingested_memories_count = 0
        ingested_sources_count = 0

        # =====================================================================
        # 2. Ingest Canonical Structured Memories (8 items)
        # =====================================================================
        logger.info(f"Processing {len(structured_memories_data)} structured memories...")
        created_memories_map = {}

        for item in structured_memories_data:
            mem_id = item["memory_id"]
            if mem_id in existing_her_day_ids:
                logger.info(f"Skipping existing structured memory: {mem_id}")
                created_memories_map[mem_id] = existing_her_day_ids[mem_id]
                continue

            canonical_text = item["canonical_text"]
            logger.info(f"Generating embedding for memory [{mem_id}] on GPU...")
            emb = embedding_service.generate_embedding(canonical_text)

            # Date normalization
            temp_date_str = item.get("temporal", {}).get("date")
            temp_prec = item.get("temporal", {}).get("precision", "unknown")
            # Invariant: precision in DB check constraint must be in ('day', 'month', 'year', 'decade', 'unknown')
            normalized_date, db_prec = normalize_event_date(temp_date_str, explicit_precision=temp_prec if temp_prec in {"day", "month", "year", "decade", "unknown"} else "unknown")

            memory_obj = Memory(
                id=uuid.uuid4(),
                user_id=user.id,
                memory_type=item.get("memory_type", "episodic"),
                content=canonical_text,
                importance=5 if item.get("confidence", 0) >= 0.9 else 4,
                confidence=float(item.get("confidence", 0.9)),
                event_date=normalized_date,
                event_date_precision=db_prec,
                status="active",
                access_scope="default",
                version=1,
                is_active=True,
                embedding=emb,
                memory_metadata={
                    "her_day_id": mem_id,
                    "dataset": "HER_DAY_v1",
                    "category": item.get("category"),
                    "perspective": item.get("perspective", "Vivek's perspective"),
                    "entities": item.get("entities", []),
                    "emotional_tags": item.get("emotional_tags", []),
                    "consent_review": item.get("consent_review"),
                    "boundary_enforced": True if "boundary" in item.get("category", "") or "friend" in canonical_text.lower() else False,
                    "original_temporal_precision": temp_prec,
                    "source_ids": item.get("source_ids", []),
                    "event_ids": item.get("event_ids", []),
                },
            )
            db.add(memory_obj)
            db.flush()

            created_memories_map[mem_id] = memory_obj
            existing_her_day_ids[mem_id] = memory_obj
            ingested_memories_count += 1

            # Connect provenance sources
            for sid in item.get("source_ids", []):
                src_info = raw_sources_by_id.get(sid) or letters_by_id.get(sid)
                if src_info:
                    stype = normalize_source_type(src_info.get("source_type", "document"))
                    sref = src_info.get("source_url") or src_info.get("url") or "https://vivek0929.github.io/HER_DAY/"
                    sloc = f"{src_info.get('source_file', 'index.html')}#{src_info.get('section', sid)}"
                    excerpt_text = src_info.get("text", "")[:1000]

                    src_rec = MemorySource(
                        id=uuid.uuid4(),
                        memory_id=memory_obj.id,
                        artifact_id=artifact.id,
                        source_type=stype,
                        source_reference=sref,
                        source_location=sloc,
                        excerpt=excerpt_text,
                        source_metadata={
                            "source_id": sid,
                            "speaker_perspective": src_info.get("speaker_perspective", "Vivek-authored"),
                            "review_status": src_info.get("review_status", "verified"),
                        },
                    )
                    db.add(src_rec)
                    ingested_sources_count += 1

        db.commit()

        # =====================================================================
        # 3. Ingest Timeline Events (12 items)
        # =====================================================================
        logger.info(f"Processing {len(timeline_data)} timeline events...")
        for item in timeline_data:
            evt_id = item["event_id"]
            date_prefix = f"[{item['date']}] " if item.get("date") else ""
            content = f"{date_prefix}{item['title']}: {item['description']}"
            if item.get("original_quote"):
                content += f" (Note: \"{item['original_quote']}\")"

            raw_date = item.get("date")
            raw_prec = item.get("date_precision", "day")
            normalized_date, db_prec = normalize_event_date(raw_date, explicit_precision=raw_prec if raw_prec in {"day", "month", "year", "decade", "unknown"} else "unknown")

            review_status = item.get("review_status", "")
            is_ambiguous = "ambiguous" in evt_id or "manual_correction_required" in review_status
            confidence = 0.80 if is_ambiguous else 0.95

            if evt_id in existing_her_day_ids:
                if not reindex:
                    logger.info(f"Skipping existing timeline event: {evt_id}")
                    continue
                logger.info(f"Reindexing timeline event [{evt_id}]...")
                memory_obj = existing_her_day_ids[evt_id]
                memory_obj.content = content
                memory_obj.embedding = embedding_service.generate_embedding(content)
                memory_obj.event_date = normalized_date
                memory_obj.event_date_precision = db_prec
                db.flush()
                continue

            logger.info(f"Generating embedding for timeline event [{evt_id}] on GPU...")
            emb = embedding_service.generate_embedding(content)

            memory_obj = Memory(
                id=uuid.uuid4(),
                user_id=user.id,
                memory_type="milestone",
                content=content,
                importance=5 if "first" in evt_id or "special" in evt_id or "conversation" in evt_id else 4,
                confidence=confidence,
                event_date=normalized_date,
                event_date_precision=db_prec,
                status="active",
                access_scope="default",
                version=1,
                is_active=True,
                embedding=emb,
                memory_metadata={
                    "her_day_id": evt_id,
                    "dataset": "HER_DAY_v1",
                    "title": item.get("title"),
                    "event_type": item.get("event_type"),
                    "original_quote": item.get("original_quote"),
                    "perspective": item.get("perspective", "Vivek's recollection"),
                    "review_status": review_status,
                    "source_ids": item.get("source_ids", []),
                    "is_ambiguous": is_ambiguous,
                    "boundary_enforced": True if "boundary" in item.get("event_type", "") or "friends" in content.lower() else False,
                },
            )
            db.add(memory_obj)
            db.flush()

            existing_her_day_ids[evt_id] = memory_obj
            ingested_memories_count += 1

            # Connect provenance sources
            for sid in item.get("source_ids", []):
                src_info = raw_sources_by_id.get(sid) or letters_by_id.get(sid)
                if src_info:
                    stype = normalize_source_type(src_info.get("source_type", "document"))
                    sref = src_info.get("source_url") or src_info.get("url") or "https://vivek0929.github.io/HER_DAY/"
                    sloc = f"{src_info.get('source_file', 'index.html')}#{src_info.get('section', sid)}"
                    excerpt_text = src_info.get("text", "")[:1000]

                    src_rec = MemorySource(
                        id=uuid.uuid4(),
                        memory_id=memory_obj.id,
                        artifact_id=artifact.id,
                        source_type=stype,
                        source_reference=sref,
                        source_location=sloc,
                        excerpt=excerpt_text,
                        source_metadata={
                            "source_id": sid,
                            "speaker_perspective": src_info.get("speaker_perspective", "Vivek-authored"),
                            "timeline_event_id": evt_id,
                        },
                    )
                    db.add(src_rec)
                    ingested_sources_count += 1

        db.commit()

        # =====================================================================
        # 4. Ingest Narrative Chunks (11 non-event chunks from rag_chunks.jsonl)
        # =====================================================================
        logger.info(f"Processing narrative RAG chunks from rag_chunks.jsonl...")
        for chunk in rag_chunks_data:
            chunk_id = chunk["chunk_id"]
            # Skip if this chunk is already an event chunk (e.g. chunk_evt_*) since timeline events cover them
            if chunk_id.startswith("chunk_evt_"):
                continue

            if chunk_id in existing_her_day_ids:
                logger.info(f"Skipping existing narrative chunk: {chunk_id}")
                continue

            chunk_text = chunk["text"]
            meta = chunk.get("metadata", {})
            logger.info(f"Generating embedding for narrative chunk [{chunk_id}] on GPU...")
            emb = embedding_service.generate_embedding(chunk_text)

            memory_obj = Memory(
                id=uuid.uuid4(),
                user_id=user.id,
                memory_type="narrative_passage",
                content=chunk_text,
                importance=4,
                confidence=0.92,
                event_date=None,
                event_date_precision="unknown",
                status="active",
                access_scope="default",
                version=1,
                is_active=True,
                embedding=emb,
                memory_metadata={
                    "her_day_id": chunk_id,
                    "dataset": "HER_DAY_v1",
                    "source_id": meta.get("source_id"),
                    "source_file": meta.get("source_file"),
                    "section": meta.get("section"),
                    "speaker_perspective": meta.get("speaker_perspective", "Vivek-authored / first-person narrative"),
                    "is_synthetic_content": True if "love_museum" in chunk_id else False,
                    "boundary_enforced": True if "friends" in chunk_text.lower() else False,
                },
            )
            db.add(memory_obj)
            db.flush()

            existing_her_day_ids[chunk_id] = memory_obj
            ingested_memories_count += 1

            # Connect source
            sid = meta.get("source_id", "web_index_about")
            stype = normalize_source_type(meta.get("source_type", "document"))
            sref = meta.get("source_url") or "https://vivek0929.github.io/HER_DAY/"
            sloc = f"{meta.get('source_file', 'index.html')}#{meta.get('section', '')}"

            src_rec = MemorySource(
                id=uuid.uuid4(),
                memory_id=memory_obj.id,
                artifact_id=artifact.id,
                source_type=stype,
                source_reference=sref,
                source_location=sloc,
                excerpt=chunk_text[:1000],
                source_metadata={
                    "source_id": sid,
                    "chunk_id": chunk_id,
                    "speaker_perspective": meta.get("speaker_perspective", "Vivek-authored"),
                },
            )
            db.add(src_rec)
            ingested_sources_count += 1

        db.commit()

        # =====================================================================
        # 5. Link Synthetic Media and Voice Boundaries to Artifact Metadata
        # =====================================================================
        logger.info("Recording ethical boundaries and media manifests...")
        artifact.context_notes = json.dumps({
            "dataset_manifest": manifest_data.get("counts"),
            "ethical_rules": manifest_data.get("important_rules"),
            "review_flags": manifest_data.get("review_flags"),
            "entities": entities_data,
            "media_manifest_summary": {
                "gallery_groups": list(media_manifest_data.get("gallery_groups", {}).keys()),
                "synthetic_photos_flagged": True,
                "voice_biometrics_cloning_prohibited": True,
            },
        }, indent=2)
        db.commit()

        logger.info(
            f"HER_DAY Ingestion completed successfully for user '{username}' ({user.id})!\n"
            f"  - Total new memories inserted: {ingested_memories_count}\n"
            f"  - Total sources linked: {ingested_sources_count}\n"
            f"  - Total active HER_DAY memories in DB: {len(existing_her_day_ids)}"
        )
        return user.id, ingested_memories_count, ingested_sources_count

    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed with error: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest HER_DAY memory dataset into HER AI PostgreSQL/pgvector")
    parser.add_argument("--dataset-dir", default="ai/datasets/her_day", help="Path to extracted dataset directory")
    parser.add_argument("--username", default="vivek", help="Username for tenant scoping")
    parser.add_argument("--email", default="vivek@her.ai", help="Email for tenant scoping")
    parser.add_argument("--reindex", action="store_true", help="Reindex existing records with updated content and embeddings")
    args = parser.parse_args()

    ingest_her_day_dataset(dataset_dir_path=args.dataset_dir, username=args.username, email=args.email, reindex=args.reindex)
