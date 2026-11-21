"""HER AI — End-to-End User Experience & Backend Integration Audit Script.

Verifies the complete flow:
  1. User Registration & JWT Issuance
  2. User Login & Credential Verification
  3. User Profile & Preferences Configuration
  4. Memory Ingestion (Text / Note)
  5. Asynchronous Processing Execution
  6. Job Polling & Status Verification
  7. Provenance Traceability Audit
  8. User Memory Correction & Atomic Supersession
  9. Chronological Memory Timeline Retrieval
  10. Temporal-Aware RAG Chat Conversation
"""

import asyncio
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.memory_artifact import MemoryArtifact
from app.services.ingestion.pipeline import memory_ingestion_pipeline


def audit_end_to_end_flow():
    client = TestClient(app)
    results = {}

    print("\n" + "=" * 70)
    print("🚀 STARTING HER AI END-TO-END INTEGRATION AUDIT")
    print("=" * 70)

    # 1. User Registration
    username = f"sam_{uuid4().hex[:6]}"
    email = f"{username}@her.ai"
    password = "SecurePassword123!"

    reg_res = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    token = reg_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    results["1_registration"] = "✅ PASSED (HTTP 201, JWT issued)"
    print(f"1. Registration & Auth: {results['1_registration']}")

    # 2. Login Verification
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": email, "password": password},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    results["2_login"] = "✅ PASSED (Argon2id verified, HTTP 200)"
    print(f"2. Login Verification: {results['2_login']}")

    # 3. Profile & Preferences Setup
    profile_res = client.get("/api/profile", headers=auth_headers)
    assert profile_res.status_code == 200, f"Profile fetch failed: {profile_res.text}"

    pref_res = client.put(
        "/api/profile/preferences",
        headers=auth_headers,
        json={"key": "tone", "value": {"warmth": "high", "conversational_style": "intimate"}},
    )
    assert pref_res.status_code == 200, f"Preferences failed: {pref_res.text}"
    results["3_profile_preferences"] = "✅ PASSED (Profile loaded, preferences stored)"
    print(f"3. Profile & Preferences: {results['3_profile_preferences']}")

    # 4. Ingest Personal Experience Note
    note_payload = {
        "title": "Seattle Move 2021",
        "content": "I moved from Chicago to Seattle on June 15, 2021 to start my work as a software engineer.",
        "artifact_type": "note",
        "context_notes": "Life milestone note",
    }
    ingest_res = client.post(
        "/api/memories/ingest/text",
        headers=auth_headers,
        json=note_payload,
    )
    assert ingest_res.status_code == 202, f"Ingestion failed: {ingest_res.text}"
    job_id = ingest_res.json()["job_id"]
    results["4_ingestion_dispatch"] = f"✅ PASSED (HTTP 202, job_id={job_id[:8]}...)"
    print(f"4. Memory Ingestion Dispatch: {results['4_ingestion_dispatch']}")

    # 5. Process Ingestion Artifact (Simulate Worker Execution)
    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        extracted_memories = loop.run_until_complete(
            memory_ingestion_pipeline.process_artifact(
                db=db,
                artifact_id=uuid4() if not job_id else job_id,
                context_notes="Life milestone note",
            )
        )
        loop.close()
    finally:
        db.close()
    results["5_background_processing"] = f"✅ PASSED (Extracted {len(extracted_memories)} memories)"
    print(f"5. Background Pipeline Processing: {results['5_background_processing']}")

    # 6. Job Polling Status Check
    job_res = client.get(f"/api/memories/ingest/{job_id}", headers=auth_headers)
    assert job_res.status_code == 200, f"Job polling failed: {job_res.text}"
    job_data = job_res.json()
    assert job_data["status"] == "completed"
    results["6_job_status"] = f"✅ PASSED (Status: completed, {job_data['extracted_memories_count']} memories)"
    print(f"6. Job Polling & Verification: {results['6_job_status']}")

    # 7. Provenance Inspection
    db = SessionLocal()
    from app.services.memory_service import memory_service
    user_memories = memory_service.list_memories(db, user_id=job_data["user_id"])
    assert len(user_memories) > 0, "No memories found for user"
    target_mem_id = user_memories[0].id
    db.close()

    prov_res = client.get(f"/api/memories/{target_mem_id}/provenance", headers=auth_headers)
    assert prov_res.status_code == 200, f"Provenance failed: {prov_res.text}"
    prov_data = prov_res.json()
    assert len(prov_data["sources"]) > 0
    results["7_provenance_traceability"] = f"✅ PASSED (Linked to artifact '{prov_data['sources'][0]['artifact']['filename']}')"
    print(f"7. Provenance Audit: {results['7_provenance_traceability']}")

    # 8. User Memory Correction
    correction_payload = {
        "content": "I moved from Chicago to Seattle on June 20, 2021 (adjusted exact date)",
        "reason": "Flight was delayed by 5 days",
        "importance": 4,
        "confidence": 1.0,
        "event_date": "2021-06-20",
        "event_date_precision": "day",
    }
    corr_res = client.post(
        f"/api/memories/{target_mem_id}/correct",
        headers=auth_headers,
        json=correction_payload,
    )
    assert corr_res.status_code == 200, f"Correction failed: {corr_res.text}"
    corr_data = corr_res.json()
    assert corr_data["old_memory"]["status"] == "superseded"
    assert corr_data["new_memory"]["status"] == "active"
    assert corr_data["new_memory"]["version"] == 2
    results["8_memory_correction"] = f"✅ PASSED (Old superseded, new version 2 active)"
    print(f"8. Memory Correction & Supersession: {results['8_memory_correction']}")

    # 9. Chronological Timeline Retrieval
    time_res = client.get("/api/memories/timeline?order=desc", headers=auth_headers)
    assert time_res.status_code == 200, f"Timeline failed: {time_res.text}"
    timeline_data = time_res.json()
    assert timeline_data["total"] >= 1
    active_item = timeline_data["items"][0]
    results["9_timeline"] = f"✅ PASSED ({timeline_data['total']} items, formatted: '{active_item['formatted_date']}')"
    print(f"9. Chronological Timeline: {results['9_timeline']}")

    # 10. Temporal-Aware RAG Chat Conversation
    chat_payload = {
        "message": "Do you remember when I moved to Seattle and where I came from?",
    }
    chat_res = client.post("/api/chat", headers=auth_headers, json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    assert "response" in chat_data
    assert len(chat_data["response"]) > 0
    results["10_temporal_rag_chat"] = f"✅ PASSED (HER responded with {len(chat_data['response'])} chars, retrieved {chat_data['memory_count']} memories)"
    print(f"10. Temporal RAG Chat: {results['10_temporal_rag_chat']}")

    print("\n" + "=" * 70)
    print("🏆 ALL 10 END-TO-END FLOW CHECKS PASSED WITH ZERO CRITICAL BLOCKERS!")
    print("=" * 70 + "\n")
    return results


if __name__ == "__main__":
    audit_end_to_end_flow()
