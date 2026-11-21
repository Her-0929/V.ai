# HER AI — Complete API Reference & Documentation

> **Document Version:** 2.1.0  
> **Date:** 2026-11-13  
> **API Version:** v0.3.0 (Milestone 11 Hardened & Verified)  
> **Base URL:** `http://localhost:8000`  
> **Interactive Swagger UI:** `http://localhost:8000/docs`  
> **ReDoc Documentation:** `http://localhost:8000/redoc`

---

## 1. Overview & Protocol Guidelines

HER AI provides a RESTful HTTP JSON API built on FastAPI. It supports authenticated conversational interaction, memory extraction, semantic retrieval, conversation history analysis, emotional intelligence, and complete user data isolation.

### Global Request Conventions
- **Content-Type:** `application/json` for all requests containing a body (except `/api/auth/token` which uses `application/x-www-form-urlencoded`).
- **Authentication:** All endpoints (except `/api/auth/register`, `/api/auth/login`, `/api/auth/token`, `/`, and `/health`) require an HTTP `Authorization` header containing a valid JWT Bearer access token:
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **User Scoping:** User identity is strictly derived from the validated JWT token claims (`current_user.id`). Client-supplied `user_id` query/body parameters have been eliminated from authorization to guarantee cross-tenant security and prevent identity spoofing.
- **Rate Limiting:**
  - `POST /api/chat`: 30 requests/minute
  - `POST /api/memories/search`: 60 requests/minute
  - Global default: 120 requests/minute
- **Timestamp Format:** ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SS.mmmmmmZ`).
- **UUID Format:** Standard RFC 4122 canonical string representation.

---

## 2. Authentication API (`/api/auth`)

### `POST /api/auth/register`
Create a new user account with Argon2id password hashing and immediate JWT issuance.

**Request Body:**
```json
{
  "username": "vivek_ai",
  "email": "vivek@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "e1b963e8-ac2d-4539-8805-23c17ec0eabe",
    "username": "vivek_ai",
    "email": "vivek@example.com",
    "created_at": "2026-11-13T06:00:00Z",
    "updated_at": "2026-11-13T06:00:00Z"
  }
}
```
*Errors:* `400 Bad Request` (validation error), `409 Conflict` (username or email already registered).

---

### `POST /api/auth/login`
Authenticate existing user via JSON body and receive a signed JWT access token.

**Request Body:**
```json
{
  "username_or_email": "vivek@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "e1b963e8-ac2d-4539-8805-23c17ec0eabe",
    "username": "vivek_ai",
    "email": "vivek@example.com",
    "created_at": "2026-11-13T06:00:00Z",
    "updated_at": "2026-11-13T06:00:00Z"
  }
}
```
*Errors:* `401 Unauthorized` (incorrect credentials), `403 Forbidden` (account deactivated).

---

### `POST /api/auth/token`
OAuth2 password request form endpoint for Swagger UI and OAuth2-compliant clients (`application/x-www-form-urlencoded`).

**Form Data:**
- `username`: Username or Email
- `password`: User password

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": { ... }
}
```

---

### `GET /api/auth/me`
Retrieve the authenticated user's current account profile.

**Headers:**
`Authorization: Bearer <access_token>`

**Response:** `200 OK`
```json
{
  "id": "e1b963e8-ac2d-4539-8805-23c17ec0eabe",
  "username": "vivek_ai",
  "email": "vivek@example.com",
  "created_at": "2026-11-13T06:00:00Z",
  "updated_at": "2026-11-13T06:00:00Z"
}
```
*Errors:* `401 Unauthorized` (missing/invalid/expired token), `403 Forbidden` (account deactivated).

---

## 3. System Endpoints

### `GET /`
Returns service status, active version, and top-level entrypoints.

**Response:** `200 OK`
```json
{
  "name": "HER AI",
  "version": "0.3.0",
  "status": "running",
  "description": "Your Personal AI Companion",
  "endpoints": {
    "docs": "/docs",
    "auth": "/api/auth",
    "chat": "POST /api/chat",
    "conversations": "/api/conversations",
    "memories": "/api/memories",
    "profile": "/api/profile",
    "health": "/health"
  }
}
```

### `GET /health`
Liveness probe endpoint.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "0.3.0"
}
```

---

## 4. Chat & Orchestration API (`/api/chat`)

### `POST /api/chat`
*Rate Limit:* `30/minute`  
*Headers:* `Authorization: Bearer <token>`

The primary conversational endpoint. Executes the 9-step RAG pipeline:
1. Validates input and persists the user message to the authenticated user's conversation.
2. Performs vector cosine-distance semantic search over the user's active memories (top-5).
3. Analyzes emotional context and historical affect blending.
4. Synthesizes a personalized prompt combining persona, retrieved memories, and emotional guidance.
5. Injects recent conversation history (up to 15 turns).
6. Dispatches to the active LLM provider (Ollama / Groq / Gemini / OpenRouter).
7. Persists the assistant's reply.
8. Enqueues an asynchronous background task to extract long-term facts and store new memories.
9. Returns the assistant's reply, retrieved memories, and detected emotion.

**Request Body:**
```json
{
  "message": "I'm thinking about switching jobs to AI research. Remember what we talked about?",
  "conversation_id": "c1f2e3d4-b5a6-4c7d-8e9f-0a1b2c3d4e5f" // optional; auto-created if omitted
}
```

**Response:** `200 OK`
```json
{
  "conversation_id": "c1f2e3d4-b5a6-4c7d-8e9f-0a1b2c3d4e5f",
  "response": "I remember you sharing that you want to become an AI engineer. Moving into AI research sounds like a wonderful continuation of that dream...",
  "retrieved_memories": [
    {
      "id": "e2a3c4b5-1234-5678-9abc-def012345678",
      "content": "User wants to become an AI engineer",
      "memory_type": "career_goal",
      "importance": 5,
      "confidence": 0.95,
      "similarity": 0.2741
    }
  ],
  "memory_count": 1,
  "model": "qwen3:1.7b",
  "emotional_context": {
    "emotion": "excitement",
    "intensity": "medium",
    "confidence": 0.72,
    "should_acknowledge": true
  }
}
```

---

## 5. Conversations API (`/api/conversations`)

*Headers:* `Authorization: Bearer <token>` on all requests.

### `GET /api/conversations`
List all conversations belonging to the authenticated user.
- **Query Params:** `limit: int = 50` (1..200)

### `POST /api/conversations`
Create a new conversation session for the authenticated user.
- **Request Body:** `{"title": "Morning Reflection"}` (optional)

### `GET /api/conversations/search`
Search conversations by title keyword matching for the authenticated user.
- **Query Params:** `q: str`, `limit: int = 20`

### `GET /api/conversations/{conversation_id}`
Retrieve full conversation metadata and complete message history. Returns `404` if not owned by the authenticated user.

### `DELETE /api/conversations/{conversation_id}`
Hard delete a conversation and all its associated messages from the database. Enforces ownership (`404` if not owned).

### `GET /api/conversations/{conversation_id}/stats`
Retrieve conversation statistics including message counts, created at, and updated at. Enforces ownership.

### `POST /api/conversations/{conversation_id}/generate-title`
Automatically generate a concise conversation title using the LLM based on conversation messages.

### `POST /api/conversations/{conversation_id}/summarize`
Generate a structured summary of the conversation using the LLM for context compression. Enforces ownership.

---

## 6. Memories API (`/api/memories`)

*Headers:* `Authorization: Bearer <token>` on all requests.

### `GET /api/memories`
List memories for the authenticated user with optional filtering.
- **Query Params:** `memory_type: str | None`, `is_active: bool = True`, `limit: int = 50`, `offset: int = 0`

### `POST /api/memories`
Manually create a new memory with vector embedding for the authenticated user.
- **Request Body:** `{"content": "Loves hiking in nature", "memory_type": "interest", "importance": 4, "confidence": 0.9}`

### `POST /api/memories/search`
*Rate Limit:* `60/minute`  
Perform pgvector cosine-distance semantic search across the authenticated user's active memories.
- **Request Body:** `{"query": "outdoor activities", "limit": 5, "min_similarity": 0.65}`

### `GET /api/memories/export`
Export all active memories for the authenticated user (JSON format).

### `DELETE /api/memories/all`
Privacy purge: permanently delete all memories belonging to the authenticated user.

### `POST /api/memories/ingest/file`
*Rate Limit:* `20/minute`  
*Content-Type:* `multipart/form-data`  
Ingest an uploaded personal artifact file (PDF document, note, letter, photo, or audio transcript).
- **Form Fields:**
  - `file: UploadFile` (binary content)
  - `artifact_type: Literal['document', 'note', 'letter', 'photo', 'audio_transcript']`
  - `context_notes: str | None` (optional user notes/context)
- **Features:** Magic signature verification, SHA-256 deduplication, background task queueing, isolated user storage.
- **Response:** `202 Accepted` (`MemoryArtifactJobResponse` containing `job_id`, `status: pending`, `file_size_bytes`, `checksum_sha256`).

### `POST /api/memories/ingest/text`
*Rate Limit:* `20/minute`  
*Content-Type:* `application/json`  
Ingest plain-text reflections, correspondence, or notes directly.
- **Request Body:**
  ```json
  {
    "title": "College Roommates",
    "content": "I lived with Dave on Elm Street in 2018.",
    "artifact_type": "note",
    "context_notes": "Reflection"
  }
  ```
- **Response:** `202 Accepted` (`MemoryArtifactJobResponse` containing `job_id`).

### `GET /api/memories/ingest/{job_id}`
Poll the status of an asynchronous memory ingestion job.
- **Response:** `200 OK` (`MemoryArtifactJobDetailResponse` containing `status`, `retry_count`, `error_message`, `processed_at`, `extracted_memories_count`, and `extracted_memory_ids`). Returns `404` if not found or unauthorized.

### `GET /api/memories/timeline`
Retrieve memories chronologically organized by event date with precision-aware formatting.
- **Query Params:**
  - `start_date: date | None`
  - `end_date: date | None`
  - `precision: str | None` (`day`, `month`, `year`, `decade`, `unknown`)
  - `include_unknown_dates: bool = True`
  - `include_superseded: bool = False`
  - `order: Literal['asc', 'desc'] = 'desc'`
  - `limit: int = 50` (1..100)
  - `offset: int = 0`
- **Response:** `200 OK` (`MemoryTimelineResponse` containing formatted items with `event_date`, `formatted_date`, `primary_source_type`, `version`, `status`).

### `GET /api/memories/{memory_id}`
Retrieve a specific memory by ID. Enforces ownership (`404` if not owned).

### `PATCH /api/memories/{memory_id}`
Update memory fields (`content`, `importance`, `confidence`, `is_active`, `metadata`). Enforces ownership.

### `DELETE /api/memories/{memory_id}`
Hard delete a specific memory from the database. Enforces ownership (`404` if not owned).

### `POST /api/memories/{memory_id}/deactivate`
Soft-delete (deactivate) a memory by setting `is_active=False`. Excludes it from standard RAG retrieval while preserving record history. Enforces ownership.

### `GET /api/memories/{memory_id}/provenance`
Retrieve complete origin traceability for an extracted memory, linking to original artifact filenames, SHA-256 checksums, exact source excerpts, page/timestamp locations, and version lineage.
- **Response:** `200 OK` (`MemoryProvenanceResponse` containing `sources` array and `history` version lineage).

### `POST /api/memories/{memory_id}/correct`
User-controlled memory correction with concurrency-safe atomic supersession.
- **Request Body:**
  ```json
  {
    "content": "User lived on Oak Street (not Elm Street) in 2018",
    "reason": "Corrected street name typo",
    "importance": 4,
    "confidence": 1.0,
    "event_date": "2018",
    "event_date_precision": "year"
  }
  ```
- **Guarantees:** Row-level locking (`with_for_update()`), version increment (`version = old.version + 1`), cycle prevention, original artifact source retention, and atomic commit.
- **Response:** `200 OK` (`MemoryCorrectionResponse` with `old_memory` marked `superseded` and `new_memory` marked `active`).

---

## 7. Profile & Preferences API (`/api/profile`)

*Headers:* `Authorization: Bearer <token>` on all requests.

### `GET /api/profile`
Retrieve authenticated user profile, preferences list, and aggregated conversation/memory counts.

### `PATCH /api/profile`
Update user profile attributes (e.g. `username`).
- **Request Body:** `{"username": "new_username"}`

### `DELETE /api/profile`
Permanently delete the authenticated user's account and all associated memories, messages, preferences, and conversations from the database.

### `GET /api/profile/export`
GDPR-compliant export of all personal data, conversations, messages, preferences, and memories belonging to the authenticated user.

### `GET /api/profile/preferences`
Retrieve all custom key-value preferences for the authenticated user.

### `PUT /api/profile/preferences`
Upsert a user preference (e.g., tone, response style, proactivity level).
- **Request Body:** `{"key": "tone", "value": {"style": "warm", "brevity": "medium"}}`

### `DELETE /api/profile/preferences/{key}`
Delete a specific user preference by key.
