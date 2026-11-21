"""Shared pytest configuration — adds backend/ to sys.path."""
import sys
import os

# Prevent HuggingFace / PyTorch network requests during test runs
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Allow `from app.xxx import ...` without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))




