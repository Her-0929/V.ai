
import torch
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Enforce GPU-only execution
if not torch.cuda.is_available():
    raise RuntimeError("HER requires an NVIDIA CUDA GPU!")

device = "cuda"

print("Loading HER embedding model...")
print("GPU:", torch.cuda.get_device_name(0))

# Load model directly onto NVIDIA GPU
model = SentenceTransformer(
    MODEL_NAME,
    device=device
)

# Test sentence
text = "I want to become an AI engineer."

# Generate embedding on GPU
embedding = model.encode(
    text,
    convert_to_tensor=True,
    normalize_embeddings=True,
    device=device
)

torch.cuda.synchronize()

# Verify actual GPU execution
assert embedding.device.type == "cuda", "Embedding was not generated on GPU!"
assert len(embedding) == 384, "Unexpected embedding dimensions!"

print("\n========== HER GPU EMBEDDING TEST ==========")
print("Original text:", text)
print("Execution device:", embedding.device)
print("Embedding dimensions:", embedding.shape[0])
print("First 10 values:", embedding[:10].cpu().tolist())
print("GPU memory allocated:",
      round(torch.cuda.memory_allocated(0) / 1024**2, 2), "MB")
print("\nHER GPU EMBEDDING SUCCESSFUL!")
