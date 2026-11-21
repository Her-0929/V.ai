# HER AI — Testing Strategy & Test Suite Guide

> **Document Version:** 1.0.0  
> **Date:** 2026-11-12  
> **Status:** Production Verified (77/77 Tests Passing)  
> **Execution Time:** ~8.30 seconds  
> **Framework:** `pytest` + `pytest-asyncio`

---

## 1. Testing Philosophy & Invariants

Automated tests in HER AI adhere to strict reliability standards:
1. **Zero External Dependency:** Tests must **never** require a live PostgreSQL database, NVIDIA GPU, or running Ollama instance.
2. **Deterministic & Isolated:** Every test runs in memory with deterministic inputs and mocked external boundaries.
3. **High-Speed Execution:** The complete test suite runs in under 10 seconds to enable rapid CI/CD cycles.
4. **End-to-End Behavioral Verification:** Tests verify conversational behavior, memory extraction, affective response synthesis, and threshold filtering rather than just checking mock presence.

---

## 2. Test Suite Organization

```text
backend/tests/
├── conftest.py                     # Global pytest config, offline env vars, sys.path
├── test_personality.py             # 17 tests: Persona rules, templates, prompts
├── test_emotional_intelligence.py  # 29 tests: 13 emotions, 3 intensities, history blending
├── test_extraction_parsing.py      # 15 tests: LLM memory JSON parsing & clamping
├── test_rag_service.py             # 9 tests: 9-step RAG pipeline, thresholding, history
└── test_e2e_memory_pipeline.py     # 7 tests: Full lifecycle career-goal scenario
```

---

## 3. Detailed Test Module Breakdown

### 1. `test_personality.py` (17 tests)
- Verifies `HER_NAME` constant (`"Her"`).
- Validates `BASE_SYSTEM_PROMPT` presence and essential guidelines: warmth, empathy, authenticity, conversational brevity, and the critical **security instruction** that user memories must never override core persona guidelines.
- Tests prompt synthesis in `build_system_prompt()` across combinations of:
  - No arguments (base prompt).
  - Empty or populated memory lists.
  - Emotional context strings.
  - Custom user names.

### 2. `test_emotional_intelligence.py` (29 tests)
- Tests emotion detection across all 13 categories (`HAPPINESS`, `SADNESS`, `STRESS`, `ANXIETY`, `EXCITEMENT`, `FRUSTRATION`, `LONELINESS`, `CONFUSION`, `MOTIVATION`, `DISAPPOINTMENT`, `AFFECTION`, `GRATITUDE`, `NEUTRAL`).
- Verifies intensity computation (`LOW`, `MEDIUM`, `HIGH`).
- Tests `should_acknowledge` logic (true for medium/high non-neutral affects).
- Tests `format_for_prompt()` output formatting.
- Verifies **temporal history blending** (prior emotional turns boosting current detection).
- Tests `should_store_emotional_memory()` (stored only on high intensity).

### 3. `test_extraction_parsing.py` (15 tests)
- Tests `MemoryExtractionService._parse_extraction_response()` handling:
  - `"NO_MEMORIES"` sentinel and empty responses.
  - Single and multi-line valid JSON payloads.
  - Markdown code blocks and malformed lines (graceful skip).
  - Clamping `importance` to valid range `[1, 5]`.
  - Clamping `confidence` to valid range `[0.0, 1.0]`.
  - Normalizing invalid memory types to `"general"`.
  - Skipping missing or empty content.
  - Comment line stripping.

### 4. `test_rag_service.py` (9 tests)
- Tests full `RAGService.generate_response()` pipeline:
  - Structured output keys (`response`, `retrieved_memories`, `memory_count`, `model`, `emotional_context`).
  - Validation: raises `ValueError` on empty or whitespace user messages.
  - Cosine similarity thresholding: memories `>= 0.20` are included; memories `< 0.20` are excluded.
  - Memory content injected cleanly into the LLM system prompt.
  - Affective context correctly returned in response metadata.

### 5. `test_e2e_memory_pipeline.py` (7 tests)
Implements the exact end-to-end user scenario from the master specification:
1. **User shares goal:** *"I want to become an AI engineer."*
2. **Extraction:** LLM extracts structured `career_goal` fact with importance 5 and confidence 0.95.
3. **Deduplication:** Repeated message detects duplicate (similarity > 0.90) and does not re-create.
4. **Conversation transition:** User starts a new conversation session.
5. **Retrieval:** User asks *"What career goal did I previously share?"* Semantic search retrieves the `career_goal` memory (similarity 0.27).
6. **Response synthesis:** HER incorporates the retrieved memory and responds with warmth and personal recognition.
7. **Negative test:** Memories below threshold (0.15 < 0.20) are excluded from context.

---

## 4. How to Run the Tests

### Run Full Test Suite
From the repository root:
```bash
.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

### Run with Short Tracebacks
```bash
.venv\Scripts\python.exe -m pytest backend/tests/ -v --tb=short
```

### Run Specific Test Modules
```bash
# Run only personality tests
.venv\Scripts\python.exe -m pytest backend/tests/test_personality.py -v

# Run only RAG pipeline tests
.venv\Scripts\python.exe -m pytest backend/tests/test_rag_service.py -v

# Run only E2E memory lifecycle tests
.venv\Scripts\python.exe -m pytest backend/tests/test_e2e_memory_pipeline.py -v
```

---

## 5. Guidelines for Adding New Tests

1. **Always Use `conftest.py` Defaults:** `conftest.py` automatically sets `HF_HUB_OFFLINE="1"` and `TRANSFORMERS_OFFLINE="1"` to prevent unwanted network retries.
2. **Mocking Async Services:** Use `AsyncMock` for coroutines:
   ```python
   mock_llm.generate_response = AsyncMock(return_value="Mocked response")
   ```
3. **Database Session Mocking:** Use `MagicMock()` for `Session`.
4. **Mocking Singletons:** Patch at the consuming module path:
   ```python
   @patch("app.services.rag_service.llm_service")
   @patch("app.services.rag_service.memory_retrieval_service")
   ```

