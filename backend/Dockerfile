FROM python:3.12-slim

WORKDIR /app

# System dependencies for psycopg binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV FASTEMBED_CACHE_PATH=/app/model_cache
RUN mkdir -p /app/model_cache && chmod -R 777 /app/model_cache

# Pre-download the fastembed ONNX model at build time into /app/model_cache
RUN python -c "from fastembed import TextEmbedding; list(TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/app/model_cache').embed(['warmup']))" && chmod -R 777 /app/model_cache

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
