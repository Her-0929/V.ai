"""
Embedding service using fastembed (ONNX runtime) with graceful zero-vector fallback.
Memory footprint: ~80 MB — compatible with Render free tier (512 MB limit).
Model: BAAI/bge-small-en-v1.5 — 384 dimensions.
"""
import os
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    MODEL_NAME = "BAAI/bge-small-en-v1.5"
    DIMENSIONS = 384

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                cache_dir = os.environ.get("FASTEMBED_CACHE_PATH", "/app/model_cache")
                self._model = TextEmbedding(model_name=self.MODEL_NAME, cache_dir=cache_dir)
                logger.info("HER Embedding Service: fastembed ready.")
            except Exception as exc:
                logger.warning("HER Embedding Service: Could not load fastembed model: %s", exc)
                return None
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        model = self._load_model()
        if model is not None:
            try:
                embeddings = list(model.embed([text]))
                embedding = embeddings[0].tolist()
                if len(embedding) == self.DIMENSIONS:
                    return embedding
            except Exception as exc:
                logger.warning("Fastembed embedding generation error: %s", exc)

        # Fallback: neutral unit-norm or zero vector so cloud runtime never crashes
        return [0.0] * self.DIMENSIONS


# Lightweight singleton
embedding_service = EmbeddingService()

