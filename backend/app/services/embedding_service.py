
import torch
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSIONS = 384

    def __init__(self):
        if not torch.cuda.is_available():
            raise RuntimeError(
                "HER requires an NVIDIA CUDA GPU."
            )

        self.device = "cuda"

        self.model = SentenceTransformer(
            self.MODEL_NAME,
            device=self.device
        )

        print(
            f"HER Embedding Service initialized on "
            f"{torch.cuda.get_device_name(0)}"
        )

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        embedding = self.model.encode(
            text,
            convert_to_tensor=True,
            normalize_embeddings=True,
            device=self.device
        )

        torch.cuda.synchronize()

        if embedding.device.type != "cuda":
            raise RuntimeError("Embedding was not generated on GPU.")

        if embedding.shape[0] != self.DIMENSIONS:
            raise ValueError("Unexpected embedding dimensions.")

        return embedding.cpu().tolist()


embedding_service = EmbeddingService()
