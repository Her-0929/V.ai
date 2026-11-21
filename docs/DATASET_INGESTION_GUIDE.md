# HER AI — Dataset Ingestion & Retrieval Guide
## HER_DAY Memory Dataset Integration (Milestone 12 Phase 2)

> **Version:** 1.0.0  
> **Target Release:** HER AI v0.4.0+  
> **Dataset Source:** [https://vivek0929.github.io/HER_DAY/](https://vivek0929.github.io/HER_DAY/)  
> **Repository:** [https://github.com/Vivek0929/HER_DAY](https://github.com/Vivek0929/HER_DAY)  

---

## 1. Architecture & Design Principles

The HER_DAY dataset integration embeds structured biographical experiences, chronological milestones, and narrative reflections into HER AI's production memory infrastructure.

### Guiding Principles:
1. **Tenant Isolation:** All records belong strictly to the tenant user (`vivek` / `vivek@her.ai`). Other users cannot view, query, or infer these memories.
2. **Provenance Traceability:** Every memory links back through `MemorySource` to its originating web section, HTML file, or letter, anchored by a root `MemoryArtifact` record.
3. **Hardware Acceleration:** All 384-dimensional embeddings are generated locally on the NVIDIA CUDA GPU using `sentence-transformers/all-MiniLM-L6-v2` in offline mode.
4. **Hybrid Retrieval:** Search combines dense vector cosine distance (`pgvector`) with explicit temporal date filtering (`extract_date_from_query`).
5. **Ethical Safeguards & Boundaries:**
   - First-person claims are explicitly attributed to Vivek's perspective.
   - The "just friends" boundary established on 12 June 2024 is strictly enforced (`boundary_enforced=True`).
   - Synthetic AI-generated images are labeled as synthetic (`is_synthetic_content=True`) and never treated as documentary evidence.
   - Voice cloning and biometric voice modeling are prohibited.

---

## 2. Ingestion Mapping Overview

| Source File | Record Count | Database Model | Key Attributes Stored |
|---|:---:|---|---|
| `ingestion_manifest.json` | 1 | `MemoryArtifact` | Checksum SHA-256, file size, status, ethical rules JSON |
| `structured_memories.json` | 8 | `Memory` | Canonical text, memory type (`episodic`, `relationship_context`, `media_association`, `semantic`), importance, confidence, pgvector embedding |
| `timeline.json` | 12 | `Memory` | Milestone type, title + description, temporal event date, date precision (`day`, `unknown`), quotes |
| `rag_chunks.jsonl` | 11 (narrative) | `Memory` | Narrative passage type, source URL, section, pgvector embedding |
| `raw_sources.json` | 12 | `MemorySource` | Source type (`document`, `note`), source location, excerpt |
| `letters.json` | 3 | `MemorySource` | Source type (`letter`), date text, full letter excerpt |
| `entities.json` | 3 | Metadata | Linked entities (`person_vivek`, `person_her`, `project_her_day`) |
| `media_manifest.json` | 7 galleries | Metadata | Synthetic image tags, audio clip boundary metadata |

**Total Database Records Ingested:**
- **31 Active Memories:** 8 canonical structured memories + 12 chronological timeline events + 11 narrative passages.
- **28 Linked Provenance Sources:** 12 raw website sections + 3 letters + 13 narrative/timeline links.
- **1 MemoryArtifact:** Primary dataset tracking container.

---

## 3. How to Run Ingestion

The ingestion script is idempotent: running it multiple times will not insert duplicate records.

### Command Execution:
```powershell
# Set PYTHONPATH to backend
$env:PYTHONPATH = "backend"

# Run ingestion script
.venv\Scripts\python.exe backend/scripts/ingest_her_day_dataset.py --username vivek --email vivek@her.ai
```

### CLI Options:
- `--dataset-dir`: Path to extracted dataset (default: `ai/datasets/her_day`).
- `--username`: Target tenant username (default: `vivek`).
- `--email`: Target tenant email (default: `vivek@her.ai`).
- `--reindex`: Optional flag to update existing memory contents and regenerate vector embeddings.

---

## 4. Retrieval & Query Verification

The integration was verified against 6 canonical benchmark queries using `backend/tests/test_her_day_retrieval.py`:

| # | Query | Retrieved Memory Content | Date / Precision | Verified Similarity |
|---|---|---|---|:---:|
| 1 | *"When did Vivek first see her?"* | Vivek recalls first seeing her board a bus on 14 April 2017. He did not know her name at that moment. | `2017-04-14` (day) | 0.5898 |
| 2 | *"When did he find her social media ID?"* | Vivek says he searched for her using her name and memory of her face, then found her social media ID on 8 August 2023. | `2023-08-08` (day) | 0.6558 |
| 3 | *"When did he confess his feelings?"* | Vivek says he expressed his romantic feelings on 12 August 2023. | `2023-08-12` (day) | 0.6300 |
| 4 | *"What happened on 12 June 2024?"* | The First Time You Talked to Me: She spoke to Vivek and suggested they remain friends. (Just friends boundary) | `2024-06-12` (day) | Date matched + 0.1333 |
| 5 | *"What does Vivek remember about their temple trips?"* | Vivek recalls going on temple trips together and says that small shared moments contributed to the growth of his feelings. | `None` (unknown) | 0.6272 |
| 6 | *"What was the significance of 9 April 2025?"* | The Most Beautiful Day: Vivek describes seeing her in person for the whole day and remembers it as especially meaningful. | `2025-04-09` (day) | Date matched + 0.2472 |

---

## 5. Automated Test Suite

Run the dedicated test suite:
```powershell
.venv\Scripts\pytest.exe backend/tests/test_her_day_retrieval.py -v
```

Expected result:
```text
============================= 12 passed in 10.20s =============================
```

### Test Coverage Summary:
- `TestHerDayDatasetIntegrity` (3 tests): Verifies artifact registration, record counts, and ethical flags.
- `TestHerDayTargetRetrieval` (6 tests): Validates vector similarity and semantic grounding for each canonical query.
- `TestHerDayTimelineAndProvenance` (3 tests): Tests chronological ordering, precision formatting, and multi-hop provenance linking.
