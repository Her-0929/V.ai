import os

# Default to offline mode for Hugging Face Hub & Transformers
# to avoid DNS / HTTP retry delays when running locally without active HF calls
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

