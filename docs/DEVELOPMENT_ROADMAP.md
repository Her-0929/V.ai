# HER AI — Development Roadmap

> **Document Version:** 1.0.0  
> **Date:** 2026-11-12  
> **Status Overview:** 1 Complete · 4 Partial · 7 Not Started  
> **Target Completion:** 12 Milestones

---

## Roadmap Executive Summary

HER AI is an empathetic personal AI companion featuring long-term memory retrieval, dynamic personality modulation, and conversational RAG. This roadmap outlines the 12 key engineering milestones required to advance HER AI from a local foundational prototype to a production-ready, secure, and multi-platform companion.

```
[M1: Database & Core] ──► [M2: Memory Pipeline] ──► [M3: RAG & Chat] ──► [M4: Personality & EQ]
                                                                                │
[M8: Cloud & CI/CD]   ◄── [M7: Web Frontend]    ◄── [M6: Auth & Sec]  ◄── [M5: APIs & History]
        │
        ▼
[M9: Voice & Speech]  ──► [M10: Mobile App]     ──► [M11: Analytics]  ──► [M12: Scale & Hardening]
```

---

## Milestone Breakdown

### Milestone 1: Database Foundation & Vector Schema
- **Status:** ✅ Complete
- **Description:** Establish the relational database schema, ORM data models, vector extensions, and database migration pipeline.
- **Accomplished Work:**
  - Implemented PostgreSQL database connection and engine in `backend/app/core/database.py`.
  - Configured Alembic and applied migrations `78ea6e759ebe` (initial schema) and `6f9db25b18bb` (`Vector(384)` column).
  - Defined SQLAlchemy models for `User`, `Conversation`, `Message`, `Memory`, `MemorySource`, and `UserPreference`.
  - Established primary keys, foreign key cascading constraints, and base single-column indexes.
- **Remaining Work:**
  - Add composite index on `memories(user_id, is_active)` for query optimization.
  - Add HNSW index (`vector_cosine_ops`) on `memories.embedding` for approximate nearest-neighbor search.

---

### Milestone 2: Embedding Generation & Memory Store
- **Status:** 🟡 Partial
- **Description:** Implement sentence transformer embeddings, semantic similarity retrieval, and comprehensive memory CRUD lifecycle management.
- **Accomplished Work:**
  - Built `EmbeddingService` in `embedding_service.py` using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
  - Built `MemoryEmbeddingService` in `memory_embedding_service.py` for batch and individual vector generation.
  - Built `MemoryRetrievalService` in `memory_retrieval_service.py` using pgvector cosine distance similarity.
  - Implemented `MemoryService` in `memory_service.py` supporting creation, soft-deletion, reactivation, and search.
- **Remaining Work:**
  - Add CPU fallback in `embedding_service.py` (`device = "cuda" if torch.cuda.is_available() else "cpu"`) to eliminate import-time crashes.
  - Add missing package declarations to `backend/requirements.txt` (`pgvector`, `sentence-transformers`, `torch`, `numpy`).
  - Implement vector deduplication logic to prevent storing redundant factual memories.

---

### Milestone 3: Conversational RAG & LLM Integration
- **Status:** 🟡 Partial
- **Description:** Connect the local Ollama LLM service with retrieved memories and conversation history into a unified response generation pipeline.
- **Accomplished Work:**
  - Built async `LLMService` in `llm_service.py` targeting Ollama (`qwen3:1.7b`).
  - Implemented `RAGService` in `rag_service.py` combining memory retrieval, threshold filtering (0.20 similarity), and prompt construction.
  - Built `ConversationService` in `conversation_service.py` for session management and message persistence.
  - Implemented `POST /api/chat` endpoint in `api/chat.py` with Pydantic request/response validation.
- **Remaining Work:**
  - Enable conversation history in RAG pipeline (`ENABLE_HISTORY = True` in `rag_service.py`).
  - Eliminate duplicate history retrieval queries in `chat.py` in favor of `conversation_service`.
  - Replace debug `print()` statements in `rag_service.py` with structured logging.
  - Sanitize API error handling to avoid returning raw exception details in 502 responses.

---

### Milestone 4: Personality Engine & Emotional Intelligence
- **Status:** 🟡 Partial
- **Description:** Infuse the companion with dynamic personality traits, sentiment awareness, and empathic response modulation.
- **Accomplished Work:**
  - Implemented comprehensive `personality.py` in `backend/app/core/` defining HER identity, core traits, tone variations, and system prompts.
  - Implemented `emotional_intelligence_service.py` in `backend/app/services/` with lightweight emotion detection across 13 emotional states.
- **Remaining Work:**
  - Wire `EmotionalIntelligenceService` into `rag_service.py` to analyze incoming messages in real time.
  - Dynamically inject emotional guidance and tone modifiers from `personality.py` into the RAG system prompt.
  - Store emotional state transitions in session metadata to maintain mood continuity across conversation turns.

---

### Milestone 5: Automatic Memory Extraction & REST Management APIs
- **Status:** 🟡 Partial
- **Description:** Automatically extract long-term facts from dialogue and provide complete REST APIs for managing memories and conversations.
- **Accomplished Work:**
  - Created `MemoryExtractionService` in `memory_extraction_service.py` with structured LLM prompts and JSON parser.
- **Remaining Work:**
  - Integrate memory extraction into `POST /api/chat` using FastAPI `BackgroundTasks` so extraction runs asynchronously after responding.
  - Create `/api/memories` REST router:
    - `GET /api/memories` (filter by type, user, search query)
    - `POST /api/memories` (manual memory creation)
    - `GET /api/memories/{id}`
    - `PATCH /api/memories/{id}`
    - `DELETE /api/memories/{id}` (soft/hard delete)
  - Create `/api/conversations` REST router:
    - `GET /api/conversations` (list user conversations with pagination)
    - `GET /api/conversations/{id}` (fetch conversation message thread)
    - `DELETE /api/conversations/{id}` (archive or delete conversation)

---

### Milestone 6: Authentication, Authorization & Security Hardening
- **Status:** ⚪ Not Started
- **Description:** Implement robust multi-user authentication, tenant isolation, access control, and API abuse defenses.
- **Remaining Work:**
  - Implement user authentication with password hashing (bcrypt / Argon2) and JWT access/refresh token issuance.
  - Replace client-provided `user_id` with verified identity extracted from JWT tokens (`Depends(get_current_user)`).
  - Add role-based or ownership-based authorization ensuring users can access only their own conversations and memories.
  - Implement request rate limiting on `/api/chat` and API endpoints using `slowapi` or Redis.
  - Add input sanitization and adversarial prompt injection defenses.
  - Implement `.env.example` sanitation guidelines and production secret management.

---

### Milestone 7: Web Frontend User Interface
- **Status:** ⚪ Not Started
- **Description:** Build an intuitive, responsive web client providing a modern conversational interface for HER AI.
- **Remaining Work:**
  - Create a modern single-page application (React / Next.js / Tailwind CSS or lightweight web components).
  - Implement chat interface with markdown rendering, streaming response display, and conversation sidebar.
  - Build memory viewer and management dashboard allowing users to inspect and manage what HER remembers.
  - Add user profile settings, persona preference selectors, and dark/light theme support.
  - Implement WebSocket or Server-Sent Events (SSE) for real-time token streaming from Ollama.

---

### Milestone 8: Deployment Containerization & CI/CD
- **Status:** ⚪ Not Started
- **Description:** Containerize the full service stack and establish automated build, test, and continuous delivery pipelines.
- **Remaining Work:**
  - Author production multi-stage `Dockerfile` for the FastAPI backend.
  - Author complete `docker-compose.yml` orchestrating PostgreSQL (with pgvector), FastAPI app, and Ollama.
  - Set up automated GitHub Actions workflow for linting (`ruff`/`flake8`), formatting (`black`), and testing (`pytest`).
  - Build mock fixtures for database sessions and LLM responses to enable full test execution in CI without a GPU.
  - Configure automated database migration execution (`alembic upgrade head`) on container startup.

---

### Milestone 9: Voice & Speech Pipeline
- **Status:** ⚪ Not Started
- **Description:** Enable natural voice interaction through low-latency speech-to-text (STT) and expressive text-to-speech (TTS).
- **Remaining Work:**
  - Integrate local or cloud STT engine (e.g., Whisper / faster-whisper) for transcribing audio inputs.
  - Integrate natural, expressive TTS engine (e.g., Piper, Coqui, or ElevenLabs API) reflecting HER's gentle and warm persona.
  - Build full-duplex voice streaming endpoint with silence detection and interruptibility.
  - Optimize audio streaming latency to achieve sub-second response times.

---

### Milestone 10: Multi-Platform Client & Mobile Support
- **Status:** ⚪ Not Started
- **Description:** Expand access to HER AI via dedicated mobile and desktop application interfaces.
- **Remaining Work:**
  - Design cross-platform mobile client (React Native / Flutter) or progressive web app (PWA).
  - Implement native mobile push notifications and ambient check-ins (e.g., morning greetings).
  - Enable offline caching for recent messages and local preferences.
  - Support background audio sessions for hands-free conversational mode.

---

### Milestone 11: Long-term Memory Evolution & Cognitive Architecture
- **Status:** ⚪ Not Started
- **Description:** Advanced cognitive capabilities including memory importance decay, contradiction resolution, and conversation summarization.
- **Remaining Work:**
  - Implement time-based memory decay scoring (recency, frequency of recall, and base importance).
  - Build memory reconciliation and contradiction resolution (detecting when new user facts supersede old ones).
  - Implement automated hierarchical conversation summarization to condense lengthy histories into dense memory artifacts.
  - Implement memory relationship graphing to connect related facts, entities, and events across time.

---

### Milestone 12: Scalability, Observability & Hardening
- **Status:** ⚪ Not Started
- **Description:** Enterprise-grade performance tuning, comprehensive telemetry, multi-LLM routing, and high-availability operations.
- **Remaining Work:**
  - Implement LLM provider abstraction layer supporting automated fallback (Ollama ➔ vLLM ➔ Cloud API).
  - Deploy distributed vector search caching via Redis.
  - Implement OpenTelemetry tracing, Prometheus metrics (`/metrics`), and structured JSON logging.
  - Conduct full penetration testing, prompt vulnerability audits, and GDPR/privacy compliance validation (data export and right-to-be-forgotten deletion workflows).

---

## Milestone Status Summary Table

| Milestone | Title | Status | Target Phase |
|---|---|---|---|
| **M1** | Database Foundation & Vector Schema | ✅ Complete | Phase 1 (Completed) |
| **M2** | Embedding Generation & Memory Store | 🟡 Partial | Phase 1 (Immediate) |
| **M3** | Conversational RAG & LLM Integration | 🟡 Partial | Phase 1 (Immediate) |
| **M4** | Personality Engine & Emotional Intelligence | 🟡 Partial | Phase 2 |
| **M5** | Memory Extraction & REST Management APIs | 🟡 Partial | Phase 2 |
| **M6** | Authentication, Authorization & Security | ⚪ Not Started | Phase 3 |
| **M7** | Web Frontend User Interface | ⚪ Not Started | Phase 3 |
| **M8** | Deployment Containerization & CI/CD | ⚪ Not Started | Phase 3 |
| **M9** | Voice & Speech Pipeline | ⚪ Not Started | Phase 4 |
| **M10** | Multi-Platform Client & Mobile Support | ⚪ Not Started | Phase 4 |
| **M11** | Long-term Memory Evolution & Cognitive Architecture | ⚪ Not Started | Phase 5 |
| **M12** | Scalability, Observability & Hardening | ⚪ Not Started | Phase 5 |
