
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSIONS = 384

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        """Lazy-load the model on first use so startup is fast."""
        if self._model is None:
            print(f"HER Embedding Service: loading model on {self.device}...")
            self._model = SentenceTransformer(
                self.MODEL_NAME,
                device=self.device
            )
            print(f"HER Embedding Service: ready on {self.device}.")
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        model = self._load_model()

        embedding = model.encode(
            text,
            convert_to_tensor=True,
            normalize_embeddings=True,
            device=self.device
        )

        if self.device == "cuda":
            torch.cuda.synchronize()

        if embedding.shape[0] != self.DIMENSIONS:
            raise ValueError("Unexpected embedding dimensions.")

        return embedding.cpu().tolist()


# Lightweight singleton — model loads on first generate_embedding() call
embedding_service = EmbeddingService()
