# HER AI — Project Audit

> **Audit Date:** 2026-11-12  
> **Auditor:** Automated Swarm Auditor  
> **Project Root:** `v:\V\Project V\V.ai`  
> **Stack:** Python 3.12 · FastAPI · PostgreSQL + pgvector · Ollama (qwen3:1.7b) · SentenceTransformers (all-MiniLM-L6-v2) · SQLAlchemy / Alembic

---

## 1. Executive Summary

HER AI is a personal AI companion with long-term memory via RAG. The **backend foundation is functional**: the database schema is migrated, vector embeddings are stored, and the single chat endpoint returns memory-augmented responses. However, the project is at approximately **Milestone 1 of 12** — the foundational layer works locally but is not yet suitable for multi-user use, testing without a GPU, or production deployment. Roughly 70% of planned capabilities are unimplemented.

---

## 2. Completed Modules

| Module | File(s) | Status | Notes |
|--------|---------|--------|-------|
| FastAPI application shell | `backend/app/main.py` | ✅ Complete | `/` and `/health` endpoints; router registered |
| Configuration | `backend/app/core/config.py` | ✅ Complete | Pydantic Settings; env-driven |
| Database connection | `backend/app/core/database.py` | ✅ Complete | SQLAlchemy engine, `SessionLocal`, `get_db()` |
| ORM models | `backend/app/models/` | ✅ Complete | `User`, `Conversation`, `Message`, `Memory`, `MemorySource`, `UserPreference` — UUIDs, FK cascades, indexes |
| DB migrations | `backend/alembic/versions/` | ✅ Complete | 2 migrations: initial schema + pgvector `Vector(384)` column |
| Embedding service | `backend/app/services/embedding_service.py` | ✅ (GPU only) | SentenceTransformer all-MiniLM-L6-v2, 384-dim; **hard-requires CUDA** |
| Memory embedding | `backend/app/services/memory_embedding_service.py` | ✅ Complete | `generate_and_store()`, `generate_missing_embeddings()` |
| Memory retrieval | `backend/app/services/memory_retrieval_service.py` | ✅ Complete | Cosine distance via pgvector; user-scoped; top-K |
| LLM service | `backend/app/services/llm_service.py` | ✅ Complete | Async HTTPX → Ollama; qwen3:1.7b; timeout=120s |
| RAG service | `backend/app/services/rag_service.py` | ✅ (partial) | Memory retrieval + filtering + prompt building + LLM call; **history disabled** |
| Conversation service | `backend/app/services/conversation_service.py` | ✅ Complete | Create / get / save / history / list / delete |
| Chat API endpoint | `backend/app/api/chat.py` | ✅ (partial) | `POST /api/chat`; memory-augmented response works; history wired but ignored |
| Chat schemas | `backend/app/schemas/chat.py` | ✅ Complete | `ChatRequest`, `ChatResponse` with Pydantic validation |

---

## 3. Partially Implemented Modules

| Module | Status | What's Missing |
|--------|--------|----------------|
| RAG service (`rag_service.py`) | 🟡 Partial | `ENABLE_HISTORY = False` — conversation history is built but never sent to the LLM. Debug `print()` statements throughout production code. |
| Chat endpoint (`api/chat.py`) | 🟡 Partial | History is retrieved from DB and formatted but discarded by RAG. No memory extraction triggered post-response. |
| Docker / deployment | 🟡 Stub | `docker-compose.yml` exists but is **empty**. No Dockerfile. |
| README | 🟡 Stub | Lists vision and stack; no setup instructions, no API docs. |
| System prompt | 🟡 Basic | Reasonable personality prompt exists; no emotional-state injection, no persona tuning. |

---

## 4. Missing Modules

| Module | Priority | Description |
|--------|----------|-------------|
| Memory extraction service | 🔴 Critical | No automatic extraction of facts from conversations after each response |
| Memory management API | 🔴 Critical | No CRUD endpoints for memories (`GET/POST/PATCH/DELETE /api/memories`) |
| Authentication / authorization | 🔴 Critical | Any UUID accepted as `user_id`; no session tokens, no JWT |
| CPU/GPU-agnostic embedding | 🔴 Critical | Service crashes on import if no CUDA GPU present |
| Personality engine | 🟠 High | No dynamic persona, tone, or mood system |
| Emotional intelligence module | 🟠 High | No sentiment detection, no emotional-state tracking |
| User profile / preference API | 🟠 High | No endpoints to manage `UserPreference` records |
| LLM provider abstraction | 🟠 High | Ollama is hardcoded; no interface for OpenAI, Anthropic, or cloud fallback |
| Conversation summary feature | 🟠 High | No summarization of long conversations; context window will overflow |
| Rate limiting | 🟡 Medium | No per-user or per-IP rate limiting on any endpoint |
| Input sanitization | 🟡 Medium | Only Pydantic length limits; no injection or adversarial-prompt guards |
| Frontend / UI | 🟡 Medium | No web or mobile interface; API-only |
| Dataset directory structure | 🟡 Medium | `ai/` directory exists but no curated training/persona datasets |
| Test suite (proper) | 🟡 Medium | All "tests" are integration scripts requiring a live DB and GPU; no unit tests, no mocks, no pytest config |
| CI/CD pipeline | 🟡 Medium | No GitHub Actions, no linting, no automated test run |
| Memory deduplication | 🟡 Medium | No duplicate-detection before storing new memories |
| Memory importance decay | 🟢 Low | No time-based decay or archiving for old memories |
| Conversation archiving | 🟢 Low | No auto-archive or export feature |

---

## 5. Bug Report

### 🔴 Critical Bugs

| # | Location | Description | Impact |
|---|----------|-------------|--------|
| B-01 | `embedding_service.py:__init__` | `torch.cuda.is_available()` check raises `RuntimeError` on CPU-only machines — fires at **import time**, crashing the entire FastAPI application on startup | App won't start without CUDA GPU |
| B-02 | `requirements.txt` | Missing: `pgvector`, `sentence-transformers`, `torch`, `numpy`, `transformers` — these are installed in `.venv` but not declared | Fresh `pip install -r requirements.txt` produces a broken environment |

### 🟠 High Bugs

| # | Location | Description | Impact |
|---|----------|-------------|--------|
| B-03 | `rag_service.py:ENABLE_HISTORY` | `ENABLE_HISTORY = False` — conversation history is retrieved from DB (wasting a query) but never passed to the LLM | AI has no context of prior messages in the same session |
| B-04 | `api/chat.py` & `conversation_service.py` | History query uses `ORDER BY created_at DESC, id DESC LIMIT n` then `.reverse()` — messages with identical `created_at` timestamps may be returned in arbitrary order, corrupting the LLM's context window | Intermittent wrong conversation order |
| B-05 | `rag_service.py` | Multiple `print()` debug statements in hot path (`generate_response`) — stdout-logging every memory and LLM payload | Performance degradation and log noise in production |

### 🟡 Medium Bugs

| # | Location | Description | Impact |
|---|----------|-------------|--------|
| B-06 | `models/memory.py` | Missing composite index `(user_id, is_active)` on `memories` table — every memory retrieval scans all user memories | Slow retrieval as memory count grows |
| B-07 | `models/memory.py` | Missing HNSW or IVFFlat index on `memories.embedding` — pgvector defaults to exact (sequential) scan | O(n) vector search instead of approximate O(log n) |
| B-08 | `api/chat.py` | `except Exception` catches all errors and returns HTTP 502 with internal error detail — leaks implementation details to clients | Information disclosure |
| B-09 | `.env` | `.env` **is in `.gitignore`** (correct), but `.env.example` does not redact the password pattern — if `.env` is ever accidentally committed, the DB password `vivek0929` is exposed | Credential leak risk |

### 🟢 Low / Code Quality

| # | Location | Description |
|---|----------|-------------|
| B-10 | All test files | Hardcoded UUID `35d636d9-fa44-4e92-9ecd-2e39a9194559` — tests only work if that specific user exists in the database |
| B-11 | `test_embeddings.py` | Standalone script, not a pytest test; no teardown; runs actual GPU |
| B-12 | `rag_service.py` | Memory similarity re-filtered in Python after pgvector query — threshold should be applied at the SQL level |
| B-13 | `api/chat.py` | No validation that `request.message` is non-empty before calling RAG (RAG does this check, but the API should validate first) |

---

## 6. Database Status

| Item | Status | Notes |
|------|--------|-------|
| Engine | ✅ PostgreSQL + psycopg3 | `postgresql+psycopg://` driver |
| pgvector extension | ✅ Installed & migrated | `Vector(384)` on `memories.embedding` |
| Schema migrations | ✅ 2/2 applied | `78ea6e759ebe` (initial) → `6f9db25b18bb` (vector) |
| Tables | ✅ All 6 created | `users`, `conversations`, `messages`, `memories`, `memory_sources`, `user_preferences` |
| Foreign key cascades | ✅ Correct | Delete cascades from user → conversations → messages / memories |
| Performance indexes | 🟡 Partial | Basic PKs and some FKs indexed; missing `(user_id, is_active)` composite and HNSW vector index |
| Connection pooling | ✅ SQLAlchemy default | Adequate for single-user local use; needs tuning for multi-user |
| Credentials in env | ✅ Properly gitignored | `.env` excluded; `.env.example` present |

---

## 7. API Status

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/` | GET | ✅ | Returns app name |
| `/health` | GET | ✅ | Health check |
| `/api/chat` | POST | 🟡 Partial | Works; history ignored; no memory extraction triggered |
| `/api/memories` | — | ❌ Missing | No memory CRUD |
| `/api/users` | — | ❌ Missing | No user management |
| `/api/conversations` | — | ❌ Missing | No conversation listing/management REST API |
| Auth (any) | — | ❌ Missing | No authentication layer |

---

## 8. AI Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| LLM: Ollama (qwen3:1.7b) | ✅ Working | Async HTTPX; 120s timeout; temperature=0.7 |
| Embedding: all-MiniLM-L6-v2 | ✅ Working (GPU only) | 384-dim; normalized; **crashes on CPU** |
| Vector store: pgvector | ✅ Working | Cosine distance; exact scan (no HNSW yet) |
| RAG pipeline | 🟡 Partial | Memory retrieval + prompt injection works; history disabled |
| Memory extraction | ❌ Missing | No post-conversation memory extraction |
| Memory deduplication | ❌ Missing | Duplicate facts will accumulate |
| Personality engine | ❌ Missing | Static system prompt only |
| Emotional intelligence | ❌ Missing | No sentiment analysis or emotional context |
| Multi-provider LLM | ❌ Missing | Ollama only; no abstraction layer |
| GPU requirement | 🔴 Blocker | CUDA mandatory; no CPU fallback; blocks CI and CPU-only deployment |

---

## 9. Security Assessment

| Risk | Severity | Detail |
|------|----------|--------|
| No authentication | 🔴 Critical | `user_id` is accepted from the request body without verification; any caller can impersonate any user |
| No authorization | 🔴 Critical | No ownership checks beyond `user_id` match in DB queries |
| No rate limiting | 🟠 High | Unlimited requests; vulnerable to abuse and resource exhaustion |
| Error detail leakage | 🟠 High | `str(error)` returned in HTTP 502 responses — may expose internal paths or SQL errors |
| Secrets management | 🟡 Medium | `.env` is gitignored correctly; `.env.example` should use placeholder values only (no real password patterns) |
| No input sanitization | 🟡 Medium | Pydantic length limits only; no prompt-injection defenses |
| No HTTPS enforcement | 🟡 Medium | No TLS config in app or compose; acceptable for local dev, not for production |
| No audit logging | 🟢 Low | No structured access logs; no failed-request tracking |

---

## 10. Recommended Development Sequence

Based on severity and dependency ordering:

### Phase 1 — Stabilize & Fix (Week 1–2)
1. **Fix B-02:** Add `pgvector`, `sentence-transformers`, `torch`, `numpy`, `transformers` to `requirements.txt`
2. **Fix B-01:** Make embedding service GPU-optional (`device = "cuda" if torch.cuda.is_available() else "cpu"`; remove `RuntimeError`)
3. **Fix B-03:** Set `ENABLE_HISTORY = True` and remove debug `print()` statements from `rag_service.py`
4. **Fix B-04:** Change history ORDER BY to `asc(Message.created_at), asc(Message.id)` — no need for `.reverse()`
5. **Fix B-06/B-07:** Add Alembic migration for `(user_id, is_active)` composite index and HNSW vector index
6. **Write `docker-compose.yml`:** PostgreSQL + pgvector + FastAPI + Ollama services

### Phase 2 — Core Features (Week 3–5)
7. **Implement memory extraction service:** Post-chat LLM-based fact extraction → store to `memories` table
8. **Add memory management API:** `GET/POST/PATCH/DELETE /api/memories/{memory_id}`
9. **Add conversation listing API:** `GET /api/conversations`, `DELETE /api/conversations/{id}`
10. **Replace test scripts with pytest:** Proper unit tests with mocks (no live DB / GPU required)

### Phase 3 — Personality & Intelligence (Week 6–9)
11. **Personality engine:** Dynamic persona system; tone/mood modulation; character consistency
12. **Emotional intelligence:** Sentiment detection; emotional-state tracking; empathic response shaping
13. **LLM provider abstraction:** Interface supporting Ollama, OpenAI, Anthropic; config-driven selection
14. **Conversation summarization:** Auto-summarize long conversations to prevent context-window overflow

### Phase 4 — Security & Auth (Week 10–11)
15. **Authentication:** JWT-based auth or session tokens; protect all endpoints
16. **Rate limiting:** Per-user limits on `/api/chat`; use `slowapi` or middleware
17. **Input sanitization:** Prompt injection guards; stricter validation beyond Pydantic

### Phase 5 — Deployment & UI (Week 12+)
18. **Frontend:** Web UI (React/Next.js or simple HTML) or mobile client
19. **CI/CD:** GitHub Actions — lint, test, build, migrate, deploy
20. **Production hardening:** HTTPS, structured logging, monitoring, secrets management (Vault/env injection)

---

## 11. File Tree (Relevant Source)

```
v:\V\Project V\V.ai\
├── .env                          (gitignored ✅)
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml            (EMPTY ⚠️)
├── README.md                     (stub ⚠️)
├── backend/
│   ├── requirements.txt          (INCOMPLETE ⚠️)
│   └── app/
│       ├── main.py               ✅
│       ├── api/
│       │   └── chat.py           🟡 partial
│       ├── core/
│       │   ├── config.py         ✅
│       │   └── database.py       ✅
│       ├── models/               ✅ (6 models)
│       ├── schemas/
│       │   └── chat.py           ✅
│       ├── services/
│       │   ├── embedding_service.py        🔴 CUDA-only
│       │   ├── memory_embedding_service.py ✅
│       │   ├── memory_retrieval_service.py ✅
│       │   ├── llm_service.py              ✅
│       │   ├── rag_service.py              🟡 history disabled
│       │   └── conversation_service.py     ✅
│       └── test_*.py             ⚠️ integration scripts, not pytest
│   └── alembic/
│       └── versions/             ✅ 2 migrations applied
├── ai/                           (empty — datasets missing)
├── docs/                         (this file)
└── scripts/
```

---

*Generated by automated swarm audit. Cross-reference with `DEVELOPMENT_ROADMAP.md` for milestone planning.*
