# HER AI — Milestone 13 Architecture Specification
## Frontend Architecture, Design System & Backend Integration

> **Document Version:** 1.0.0  
> **Date:** 2026-11-22  
> **Status:** Architecture Proposal & Implementation Plan  
> **Target Release:** HER AI v0.5.0 (Frontend & Companion Experience)  
> **Backend Baseline:** HER AI v0.4.0 (Milestones 1–12 Complete, 137 Tests Passing)  

---

## 1. Executive Vision & Design Philosophy

HER AI is an emotionally intelligent, memory-aware personal AI companion inspired by Samantha (*Her*). The frontend interface must reflect warmth, intimacy, and calm minimalism rather than the cold, mechanical aesthetic of enterprise dashboards or standard chatbot clones.

### Core Design Tenets
1. **Emotional Warmth & Organic Palette:** Warm neutral tones (creams, warm sands, terracotta accents, soft rose-gold, muted obsidian for dark elements) create an inviting, human sanctuary.
2. **Typography & Readability:** Serif and elegant sans-serif combinations providing literary cadence and comfortable conversational reading.
3. **Clutter-Free Minimalism:** Chrome fades into the background; thoughts, memories, and voice take center stage.
4. **Radical Transparency (Provenance-First):** Every memory HER recalls can be traced back to its exact origin (personal letters, uploaded journals, conversations) with a single tap.
5. **Human Agency & Reciprocal Respect:** Memories are never permanently unalterable; users can inspect, correct, dispute, or deactivate memories with explicit version history.

---

## 2. Technology Stack & Tooling

| Layer | Selection | Justification |
|---|---|---|
| **Framework** | Next.js (App Router, React 19) | Server/Client hybrid architecture, optimal route grouping, performant layout caching. |
| **Language** | TypeScript | Strict type safety aligned 1:1 with backend Pydantic schemas. |
| **Styling** | Tailwind CSS | Utility-first ergonomic styling, fluid responsive layouts, customizable design tokens. |
| **Icons** | Lucide React | Clean, minimalist, modern iconography with expressive stroke weights. |
| **Markdown** | `react-markdown` | Safe, sanitized rendering of AI responses, formatting, and notes. |
| **API Client** | Centralized Fetch / Axios Client | Tenant-aware JWT Bearer authorization, request deduplication, uniform error handling. |
| **State Management** | React Context (`Auth`, `Toast`) | Lightweight, zero-dependency, context-isolated state without boilerplate. |

---

## 3. Application Architecture & Navigation

The frontend is structured around 5 canonical navigation destinations:

```
┌─────────────────────────────────────────────────────────────┐
│                       HER AI Frontend                       │
└──────┬──────────────┬──────────────┬──────────────┬─────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
1. Home / Chat  2. Timeline   3. Explorer   4. Ingestion   5. Profile
 - Conversations - Chronology  - Search       - File upload - Metrics
 - RAG Grounding - Precision   - Provenance   - Text notes  - Settings
 - EQ Sentiment  - Groupings   - Corrections  - Job Polling - GDPR Export
```

### Route Map
- `/`: Chat interface with conversation drawer, streaming message view, and active RAG indicator.
- `/timeline`: Chronological memory feed grouped by year/month with temporal precision chips.
- `/memories`: Full-text & semantic vector memory explorer with provenance modal and in-place correction.
- `/ingest`: Personal artifact ingestion center (PDF/TXT uploads and reflective note drafting) with live status tracking.
- `/profile`: User companion profile, memory and conversation metrics, preferences manager, and privacy controls.

---

## 4. Backend API Integration Map

The frontend connects directly to the HER AI backend at `http://localhost:8000`:

| Frontend Feature | Backend REST Endpoint | Method | Payload / Response |
|---|---|:---:|---|
| **User Authentication** | `/api/auth/login` / `/register` | `POST` | `UserLogin` / `UserRegister` → `AuthResponse` (JWT token) |
| **Identity Verification** | `/api/auth/me` | `GET` | Bearer Token → `UserResponse` |
| **RAG AI Chat** | `/api/chat` | `POST` | `ChatRequest` → `ChatResponse` (with emotional context & grounding) |
| **Conversation Threads** | `/api/conversations` | `GET`, `POST` | List & Create conversations |
| **Thread History** | `/api/conversations/{id}` | `GET`, `DELETE` | Message thread retrieval & deletion |
| **Memory Timeline** | `/api/memories/timeline` | `GET` | Precision-aware chronological items |
| **Memory Search** | `/api/memories/search` | `POST` | Vector semantic search |
| **Memory CRUD** | `/api/memories`, `/{id}` | `GET`, `POST`, `PATCH`, `DELETE` | Full memory lifecycle |
| **Memory Provenance** | `/api/memories/{id}/provenance` | `GET` | Audit trail with excerpts, page/locations & artifacts |
| **Memory Correction** | `/api/memories/{id}/correct` | `POST` | Atomic supersession with reason attribution |
| **File Ingestion** | `/api/memories/ingest/file` | `POST` (multipart) | PDF/TXT upload → Background Job ID |
| **Text Ingestion** | `/api/memories/ingest/text` | `POST` | Note content & context notes → Job ID |
| **Job Polling** | `/api/memories/ingest/{job_id}` | `GET` | Status (`pending`, `processing`, `completed`, `failed`) |
| **User Profile & Stats** | `/api/profile` | `GET`, `PATCH` | Profile metrics, username update |
| **Preferences** | `/api/profile/preferences` | `PUT`, `DELETE` | Preference key-value configuration |
| **Privacy Export** | `/api/profile/privacy-export` | `GET` | Full GDPR data dump |

---

## 5. Security & Tenant Isolation Invariants

1. **Strict User Scoping:** All API requests automatically pass `Authorization: Bearer <token>`. Cross-user data leakage is strictly blocked at the backend.
2. **Stored Credentials:** JWT access tokens are saved in secure client storage and refreshed on application mount.
3. **Graceful Offline Fallback:** When the backend or LLM is offline or processing, the UI gracefully informs the user with actionable diagnostics rather than crashing or blank-screening.
4. **Content Sanitization:** Text, markdown, and user reflections are rendered safely without raw HTML injection.
