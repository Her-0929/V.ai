# HER AI — Deployment & Operations Guide

> **Document Version:** 1.0.0  
> **Date:** 2026-11-12  
> **Status:** Production Reference  
> **Target Environments:** Local Workstation (Bare-Metal), Docker Compose, Cloud / VPS

---

## 1. System Requirements & Hardware Sizing

HER AI is optimized for low-latency operation on accessible consumer hardware.

### Hardware Baseline (Verified in Production)
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM) with CUDA 12+
- **System Memory:** 16 GB DDR4/DDR5 RAM
- **Storage:** 20 GB free NVMe SSD storage (PostgreSQL data + local LLM weights + embeddings)
- **CPU:** 4+ cores (Intel Core i5/i7 or AMD Ryzen 5/7)
- **Operating System:** Windows 10/11, Ubuntu 22.04/24.04 LTS, or macOS (CPU mode)

### Software Prerequisites
- **Python:** 3.12+
- **PostgreSQL:** 16+ with `pgvector` extension installed
- **Ollama:** 0.3.0+ running locally (`http://localhost:11434`)
- **Git**

---

## 2. Local Bare-Metal Installation (Step-by-Step)

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone <repo-url> V.ai
cd V.ai

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Step 3: PostgreSQL & pgvector Setup
Ensure PostgreSQL is running locally on port `5432`. Create the target database:
```sql
CREATE DATABASE her_ai_db;
\c her_ai_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` in the project root:
```bash
cp .env.example .env
```
Ensure database connection and provider settings match your local environment:
```ini
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/her_ai_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:1.7b
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=384
LLM_PROVIDER=ollama
LLM_ENABLE_FALLBACK=true
```

### Step 5: Run Database Migrations
Apply all schema changes and performance vector indexes (including HNSW):
```bash
cd backend
alembic upgrade head
cd ..
```

### Step 6: Pull Ollama Model
Ensure Ollama is running, then pull the default model:
```bash
ollama pull qwen3:1.7b
```

### Step 7: Launch the Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` to interact with Swagger UI.

---

## 3. Docker Compose Deployment

For containerized environments with NVIDIA Container Toolkit installed, use `docker-compose.yml`:

```yaml
version: "3.8"

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: her_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: her_password
      POSTGRES_DB: her_ai_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d her_ai_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: her_ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: her_backend
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:her_password@postgres:5432/her_ai_db
      OLLAMA_BASE_URL: http://ollama:11434
      OLLAMA_MODEL: qwen3:1.7b
      LLM_PROVIDER: ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  pgdata:
  ollama_models:
```

Launch with:
```bash
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec ollama ollama pull qwen3:1.7b
```

---

## 4. Headless Cloud & VPS Deployment (CPU / Cloud LLM Mode)

When deploying to lightweight cloud instances without dedicated NVIDIA GPUs (e.g., Render, Railway, AWS t3.medium):

1. **Database:** Use a managed PostgreSQL service supporting pgvector (e.g., Supabase, Neon, AWS RDS).
2. **Embeddings:** When running on CPU, `EmbeddingService` generates embeddings via PyTorch CPU runtime without modification.
3. **LLM Provider:** Configure cloud LLM fallback in `.env`:
   ```ini
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_groq_api_key
   LLM_ENABLE_FALLBACK=true
   GEMINI_API_KEY=AIzaSy...
   ```
   Groq delivers 400+ tokens/second latency on `llama-3.1-8b-instant`, eliminating local VRAM requirements while keeping response times under 500ms.

---

## 5. Operational Maintenance & Health Monitoring

### Health Checks
- **HTTP Health Probe:** `GET /health` returns `200 OK` with status `healthy`.
- **Database Connectivity:** Checked via `SELECT 1` in `check_db.py`.
- **Vector Index Health:** Verify HNSW index usage via `EXPLAIN ANALYZE SELECT ... ORDER BY embedding <=> query_vector LIMIT 5`.

### Backup & Disaster Recovery
- **Database Backup:**
  ```bash
  pg_dump -U postgres -d her_ai_db -F c -b -v -f her_ai_db_backup.dump
  ```
- **Database Restore:**
  ```bash
  pg_restore -U postgres -d her_ai_db -v her_ai_db_backup.dump
  ```
- **User Privacy Export:** Users can self-backup at any time via `GET /api/profile/export`.

