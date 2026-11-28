
import os
os.environ.setdefault("HF_HUB_OFFLINE", "0")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")

import torch
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSIONS = 384

    def __init__(self):
        # Use GPU if available, fall back to CPU for cloud/CPU-only deployments
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = SentenceTransformer(
            self.MODEL_NAME,
            device=self.device
        )

        if self.device == "cuda":
            print(
                f"HER Embedding Service initialized on GPU: "
                f"{torch.cuda.get_device_name(0)}"
            )
        else:
            print("HER Embedding Service initialized on CPU (cloud/no-GPU mode).")

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        embedding = self.model.encode(
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


embedding_service = EmbeddingService()
