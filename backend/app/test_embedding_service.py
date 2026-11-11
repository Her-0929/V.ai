
from app.services.embedding_service import embedding_service
import torch

text = "I want to become an AI engineer."

embedding = embedding_service.generate_embedding(text)

print("\n========== HER EMBEDDING SERVICE TEST ==========")
print("GPU:", torch.cuda.get_device_name(0))
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
print("GPU memory:", round(
    torch.cuda.memory_allocated(0) / 1024**2, 2
), "MB")

assert len(embedding) == 384

print("\nHER EMBEDDING SERVICE WORKING SUCCESSFULLY!")
