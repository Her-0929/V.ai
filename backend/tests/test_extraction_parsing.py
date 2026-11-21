"""
Tests for memory extraction response parsing.
No live DB, GPU, or Ollama required — all external deps are mocked.
"""
import sys
import pytest
from unittest.mock import patch, MagicMock

# ─── Mock heavy dependencies before importing the service ───────────────────
_mock_emb = MagicMock()
_mock_emb.generate_embedding.return_value = [0.1] * 384

_mock_llm = MagicMock()

from app.services.memory_extraction_service import MemoryExtractionService



@pytest.fixture(autouse=True)
def patch_llm():
    with patch("app.services.memory_extraction_service.llm_service", _mock_llm):
        yield


@pytest.fixture
def svc():
    return MemoryExtractionService()


# ──────────────────────────────────────────────────────────────────────────────
# _parse_extraction_response
# ──────────────────────────────────────────────────────────────────────────────

def test_parse_no_memories(svc):
    result = svc._parse_extraction_response("NO_MEMORIES")
    assert result == []


def test_parse_empty_string(svc):
    result = svc._parse_extraction_response("")
    assert result == []


def test_parse_single_valid_json(svc):
    response = (
        '{"content": "User wants to become an AI engineer", '
        '"memory_type": "career_goal", "importance": 5, '
        '"confidence": 0.95, "excerpt": "I want to be an AI engineer"}'
    )
    result = svc._parse_extraction_response(response)
    assert len(result) == 1
    assert result[0]["content"] == "User wants to become an AI engineer"
    assert result[0]["memory_type"] == "career_goal"
    assert result[0]["importance"] == 5
    assert result[0]["confidence"] == 0.95


def test_parse_multiple_lines(svc):
    response = "\n".join([
        '{"content": "User likes Python", "memory_type": "like", "importance": 3, "confidence": 0.9, "excerpt": "love Python"}',
        '{"content": "User lives in India", "memory_type": "personal_info", "importance": 2, "confidence": 0.8, "excerpt": "from India"}',
    ])
    result = svc._parse_extraction_response(response)
    assert len(result) == 2


def test_parse_invalid_json_lines_skipped(svc):
    response = "\n".join([
        '{"content": "valid fact", "memory_type": "general", "importance": 2, "confidence": 0.9, "excerpt": "x"}',
        "this is definitely not json",
        '{"content": "also valid", "memory_type": "like", "importance": 1, "confidence": 0.7, "excerpt": "y"}',
    ])
    result = svc._parse_extraction_response(response)
    assert len(result) == 2


def test_parse_importance_clamped_to_max(svc):
    response = '{"content": "test", "memory_type": "general", "importance": 99, "confidence": 0.5, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert result[0]["importance"] == 5


def test_parse_importance_clamped_to_min(svc):
    response = '{"content": "test", "memory_type": "general", "importance": -5, "confidence": 0.5, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert result[0]["importance"] == 1


def test_parse_confidence_clamped_above_one(svc):
    response = '{"content": "test", "memory_type": "general", "importance": 2, "confidence": 2.5, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert result[0]["confidence"] <= 1.0


def test_parse_confidence_clamped_below_zero(svc):
    response = '{"content": "test", "memory_type": "general", "importance": 2, "confidence": -0.5, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert result[0]["confidence"] >= 0.0


def test_parse_invalid_memory_type_becomes_general(svc):
    response = '{"content": "test", "memory_type": "completely_invalid_xyz", "importance": 2, "confidence": 0.8, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert result[0]["memory_type"] == "general"


def test_parse_valid_memory_types_preserved(svc):
    for mtype in ["career_goal", "like", "personal_info", "milestone", "life_event"]:
        response = f'{{"content": "test", "memory_type": "{mtype}", "importance": 3, "confidence": 0.8, "excerpt": "x"}}'
        result = svc._parse_extraction_response(response)
        assert result[0]["memory_type"] == mtype


def test_parse_missing_content_skipped(svc):
    response = '{"memory_type": "general", "importance": 2, "confidence": 0.8, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert len(result) == 0


def test_parse_empty_content_skipped(svc):
    response = '{"content": "", "memory_type": "general", "importance": 2, "confidence": 0.8, "excerpt": "test"}'
    result = svc._parse_extraction_response(response)
    assert len(result) == 0


def test_parse_comment_lines_skipped(svc):
    response = "\n".join([
        "# This is a comment",
        '{"content": "real fact", "memory_type": "general", "importance": 2, "confidence": 0.8, "excerpt": "x"}',
    ])
    result = svc._parse_extraction_response(response)
    assert len(result) == 1


def test_parse_whitespace_only_response(svc):
    result = svc._parse_extraction_response("   \n\n   ")
    assert result == []

