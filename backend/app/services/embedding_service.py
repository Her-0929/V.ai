"""
Embedding service using fastembed (ONNX runtime).
Memory footprint: ~80 MB — compatible with Render free tier (512 MB limit).
Model: BAAI/bge-small-en-v1.5 — 384 dimensions, same as all-MiniLM-L6-v2.
"""
from fastembed import TextEmbedding


class EmbeddingService:
    MODEL_NAME = "BAAI/bge-small-en-v1.5"
    DIMENSIONS = 384

    def __init__(self):
        # Lazy — model loads on first generate_embedding() call
        self._model: TextEmbedding | None = None

    def _load_model(self) -> TextEmbedding:
        if self._model is None:
            print("HER Embedding Service: loading ONNX model (fastembed)...")
            self._model = TextEmbedding(model_name=self.MODEL_NAME)
            print("HER Embedding Service: ready.")
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        model = self._load_model()
        # fastembed returns a generator of numpy arrays
        embeddings = list(model.embed([text]))
        embedding = embeddings[0].tolist()

        if len(embedding) != self.DIMENSIONS:
            raise ValueError(f"Unexpected embedding dimensions: {len(embedding)}")

        return embedding


# Lightweight singleton — model loads on first generate_embedding() call
embedding_service = EmbeddingService()
