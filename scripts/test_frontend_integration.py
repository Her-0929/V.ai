"""HER AI — Milestone 13 Frontend API Integration Test Suite
Simulates the Next.js frontend API client (`src/lib/api.ts`) executing against the live FastAPI backend.
"""

import sys
import os
from uuid import UUID

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

def run_frontend_integration_suite():
    print("=" * 80)
    print("HER AI — MILESTONE 13 FRONTEND INTEGRATION VERIFICATION")
    print("=" * 80)

    client = TestClient(app)

    # 1. User Authentication
    print("\n[Step 1] Authenticating tenant 'vivek' (POST /api/auth/login)...")
    login_res = client.post("/api/auth/login", json={
        "username_or_email": "vivek",
        "password": "HerAiVivekSecure2026!"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    user = login_res.json()["user"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  ✓ Logged in as: {user['username']} ({user['id']})")
    print(f"  ✓ Access token issued (len={len(token)})")

    # 2. Identity Verification
    print("\n[Step 2] Identity Verification (GET /api/auth/me)...")
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["id"] == user["id"]
    print("  ✓ Session authenticated and verified")

    # 3. Conversation Management
    print("\n[Step 3] Conversation Lifecycle (POST & GET /api/conversations)...")
    create_conv_res = client.post("/api/conversations", json={
        "title": "M13 Frontend Verification Session"
    }, headers=headers)
    assert create_conv_res.status_code == 201
    conv_id = create_conv_res.json()["id"]
    print(f"  ✓ Conversation created: {conv_id}")

    list_conv_res = client.get("/api/conversations", headers=headers)
    assert list_conv_res.status_code == 200
    assert any(c["id"] == conv_id for c in list_conv_res.json()["conversations"])
    print(f"  ✓ Conversation listed in user thread history (total: {list_conv_res.json()['total']})")

    # 4. RAG Chat Interaction
    print("\n[Step 4] RAG Chat Interaction (POST /api/chat)...")
    chat_res = client.post("/api/chat", json={
        "conversation_id": conv_id,
        "message": "When did you first see me?"
    }, headers=headers)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    assert chat_data["conversation_id"] == conv_id
    assert "response" in chat_data and len(chat_data["response"]) > 0
    assert "retrieved_memories" in chat_data
    assert "emotional_context" in chat_data
    print(f"  ✓ HER response generated: \"{chat_data['response'][:70]}...\"")
    print(f"  ✓ Grounded with {chat_data['memory_count']} memories (model: {chat_data['model']})")
    if chat_data["emotional_context"]:
        print(f"  ✓ Emotional Context: {chat_data['emotional_context']['emotion']} ({chat_data['emotional_context']['intensity']})")

    # 5. Memory Timeline Retrieval
    print("\n[Step 5] Memory Timeline Chronology (GET /api/memories/timeline)...")
    timeline_res = client.get("/api/memories/timeline?order=asc&limit=50", headers=headers)
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert timeline_data["total"] >= 31, f"Expected >= 31 memories, got {timeline_data['total']}"
    print(f"  ✓ Retrieved {len(timeline_data['items'])} chronological timeline items (total: {timeline_data['total']})")
    first_item = timeline_data["items"][0]
    print(f"  ✓ Earliest Event: [{first_item['formatted_date']}] {first_item['content'][:60]}...")

    # 6. Memory Explorer: Vector Semantic Search
    print("\n[Step 6] Memory Explorer Vector Search (POST /api/memories/search)...")
    search_res = client.post("/api/memories/search", json={
        "query": "temple visit memories",
        "limit": 5,
        "min_similarity": 0.20
    }, headers=headers)
    assert search_res.status_code == 200
    search_results = search_res.json()["results"]
    assert len(search_results) > 0
    print(f"  ✓ Found {len(search_results)} semantically similar memories for 'temple visit memories'")
    target_memory_id = search_results[0]["id"]
    print(f"  ✓ Top Match: \"{search_results[0]['content'][:60]}...\" (similarity: {search_results[0]['similarity']:.2f})")

    # 7. Memory Provenance Audit Trail
    print(f"\n[Step 7] Memory Provenance Audit (GET /api/memories/{target_memory_id}/provenance)...")
    prov_res = client.get(f"/api/memories/{target_memory_id}/provenance", headers=headers)
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert prov_data["memory_id"] == target_memory_id
    assert "sources" in prov_data
    assert "history" in prov_data
    print(f"  ✓ Provenance resolved: version {prov_data['version']}, status={prov_data['status']}")
    print(f"  ✓ Attributed Sources: {len(prov_data['sources'])}, Version History entries: {len(prov_data['history'])}")

    # 8. Memory Ingestion: Text Note & Letter
    print("\n[Step 8] Personal Data Ingestion (POST /api/memories/ingest/text)...")
    ingest_res = client.post("/api/memories/ingest/text", json={
        "title": "Autumn Reflection 2026",
        "content": "On 22 November 2026, Vivek completed the frontend interface for HER AI, uniting memory, timeline, and emotional resonance.",
        "artifact_type": "note",
        "context_notes": "Milestone 13 verification reflection"
    }, headers=headers)
    assert ingest_res.status_code == 202
    job_id = ingest_res.json()["job_id"]
    print(f"  ✓ Ingestion job dispatched (202 Accepted): Job ID = {job_id}")

    # 9. Ingestion Job Polling
    print(f"\n[Step 9] Ingestion Job Polling (GET /api/memories/ingest/{job_id})...")
    job_res = client.get(f"/api/memories/ingest/{job_id}", headers=headers)
    assert job_res.status_code == 200
    job_data = job_res.json()
    print(f"  ✓ Job status: {job_data['status']}, Artifact: {job_data['filename']}")

    # 10. Profile & Settings
    print("\n[Step 10] Profile Metrics & Preferences (GET /api/profile)...")
    prof_res = client.get("/api/profile", headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    print(f"  ✓ Profile: {prof_data['user']['username']}")
    print(f"  ✓ Memory Count: {prof_data['memory_count']}, Conversation Count: {prof_data['conversation_count']}")

    # 11. Preference Update
    print("\n[Step 11] Preference Configuration (PUT & DELETE /api/profile/preferences)...")
    pref_put_res = client.put("/api/profile/preferences", json={
        "key": "frontend_theme",
        "value": {"theme": "warm-neutral", "font": "serif"}
    }, headers=headers)
    assert pref_put_res.status_code == 200
    print("  ✓ Set preference 'frontend_theme'")

    pref_del_res = client.delete("/api/profile/preferences/frontend_theme", headers=headers)
    assert pref_del_res.status_code == 200
    print("  ✓ Cleaned up test preference 'frontend_theme'")

    # 12. GDPR Privacy Archive Export
    print("\n[Step 12] GDPR Privacy Archive Export (GET /api/profile/export)...")
    gdpr_res = client.get("/api/profile/export", headers=headers)
    assert gdpr_res.status_code == 200
    gdpr_data = gdpr_res.json()
    assert gdpr_data["total_memories"] >= 31
    print(f"  ✓ GDPR export generated with {gdpr_data['total_memories']} memories and user profile.")

    print("\n" + "=" * 80)
    print("ALL 12 FRONTEND API INTEGRATION STEPS VERIFIED SUCCESSFULLY (100% PASS)")
    print("=" * 80)

if __name__ == "__main__":
    run_frontend_integration_suite()
