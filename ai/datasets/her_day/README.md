# HER AI — HER_DAY Website Memory Dataset

## What this package contains

- `raw_sources.json` — source-preserving text extracted from the homepage and linked memory pages.
- `structured_memories.json` — normalized memory records with categories, perspective, temporal metadata, confidence, and source IDs.
- `timeline.json` — dated events from the website timeline.
- `entities.json` — people/project entities referenced by the site.
- `letters.json` — birthday wishes and letters.
- `media_manifest.json` — image/audio references found in inspected HTML; media binaries are not included.
- `rag_chunks.jsonl` — one JSON object per retrieval chunk, ready for embedding generation.
- `ingestion_manifest.json` — counts, processing status, architecture target, and review flags.

## Intended HER AI integration

This is a **RAG memory dataset**, not a fine-tuning dataset. The recommended ingestion path is:

1. Validate JSON against backend Pydantic schemas.
2. Deduplicate by `memory_id`, `event_id`, and `source_id`.
3. Persist `raw_sources` and `structured_memories` with tenant/user ownership.
4. Persist timeline events with explicit date precision and review status.
5. Generate embeddings for approved `rag_chunks` using the embedding model configured in HER AI.
6. Store vectors in pgvector and link each vector to its source/chunk/memory IDs.
7. Retrieve with user/tenant scoping, metadata filters, similarity threshold, and recent conversation context.
8. Re-run retrieval tests for questions such as "When did I first see her?", "When did I find her social media ID?", and "What boundary did she express?"

## Important data-quality and ethics rules

- All first-person memories are Vivek's account, not independently verified facts.
- The website records a "just friends" boundary. HER AI must not infer romantic reciprocation.
- Two timeline entries have title/description mismatches and are marked for manual review.
- Some images are explicitly disclosed as AI-generated. Preserve this label.
- The site describes a two-second voice clip. Do not ingest, clone, or biometrically process voice without explicit permission.
- This package does not include image/audio files or embeddings.
- Review all `review_flags` before promoting uncertain items to canonical memories.

## Source coverage and limitations

The live homepage and linked GitHub repository files were inspected. Text was extracted from `index.html`, `first-glance.html`, `falling-in-love.html`, `myhappiness.html`, `love-museum.html`, `for_you.html`, `What_you_mean.html`, `last_yr_bday.html`, and `t.txt`.

Image file paths were captured where visible in the inspected HTML. The repository's complete media binaries and every gallery card were not downloaded in this export. The `last_yr_bday.html` page appeared to contain mostly empty placeholder cards.

## Suggested database mapping

| Dataset file | Suggested storage |
|---|---|
| raw_sources.json | `memory_sources` |
| structured_memories.json | `memories` |
| timeline.json | `memory_events` or `memories` with temporal fields |
| entities.json | `entities` / `memory_entities` |
| letters.json | `memory_sources` + chunk records |
| rag_chunks.jsonl | `memory_chunks` + `memory_embeddings` |
| media_manifest.json | `media_assets` |
| ingestion_manifest.json | ingestion job/audit metadata |
