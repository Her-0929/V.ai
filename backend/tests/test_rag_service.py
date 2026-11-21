"""
Tests for the RAG service pipeline.
All external dependencies (LLM, DB, embeddings) are mocked.
No live Ollama, GPU, or database required.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

from app.services.emotional_intelligence_service import (
    Emotion,
    EmotionalIntensity,
    EmotionalContext,
)


def _neutral_ctx():
    return EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user_id():
    return uuid4()


# ──────────────────────────────────────────────────────────────────────────────
# Basic pipeline
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_generate_response_returns_expected_keys(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = []
    mock_llm.generate_response = AsyncMock(return_value="Hello!")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="Hello"
    )

    assert "response" in result
    assert "retrieved_memories" in result
    assert "memory_count" in result
    assert "model" in result
    assert "emotional_context" in result


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_generate_response_calls_llm(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = []
    mock_llm.generate_response = AsyncMock(return_value="I'm here!")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="Hi there"
    )

    mock_llm.generate_response.assert_awaited_once()
    assert result["response"] == "I'm here!"


@pytest.mark.asyncio
async def test_generate_response_raises_on_empty_message(mock_db, user_id):
    from app.services.rag_service import RAGService
    with pytest.raises(ValueError, match="[Ee]mpty|empty"):
        await RAGService().generate_response(
            db=mock_db, user_id=user_id, user_message=""
        )


@pytest.mark.asyncio
async def test_generate_response_raises_on_whitespace_message(mock_db, user_id):
    from app.services.rag_service import RAGService
    with pytest.raises(ValueError):
        await RAGService().generate_response(
            db=mock_db, user_id=user_id, user_message="   "
        )


# ──────────────────────────────────────────────────────────────────────────────
# Memory filtering
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_memory_above_threshold_included(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = [
        {"id": "1", "content": "AI engineer goal", "memory_type": "career_goal",
         "importance": 5, "confidence": 1.0, "similarity": 0.35},
    ]
    mock_llm.generate_response = AsyncMock(return_value="I remember!")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="What are my goals?"
    )
    assert result["memory_count"] == 1
    assert result["retrieved_memories"][0]["content"] == "AI engineer goal"


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_memory_below_threshold_excluded(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = [
        {"id": "1", "content": "irrelevant fact", "memory_type": "general",
         "importance": 1, "confidence": 0.5, "similarity": 0.05},
    ]
    mock_llm.generate_response = AsyncMock(return_value="Hello!")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="Hi"
    )
    assert result["memory_count"] == 0


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_mixed_memories_filtered_correctly(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = [
        {"id": "1", "content": "above", "memory_type": "career_goal",
         "importance": 5, "confidence": 1.0, "similarity": 0.30},
        {"id": "2", "content": "below", "memory_type": "general",
         "importance": 1, "confidence": 0.5, "similarity": 0.10},
    ]
    mock_llm.generate_response = AsyncMock(return_value="Got it!")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="Tell me about myself"
    )
    assert result["memory_count"] == 1
    assert result["retrieved_memories"][0]["content"] == "above"


# ──────────────────────────────────────────────────────────────────────────────
# Memory injected into system prompt
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_memory_content_in_system_prompt(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    mock_retrieval.search_similar_memories.return_value = [
        {"id": "1", "content": "User loves jazz music", "memory_type": "like",
         "importance": 3, "confidence": 1.0, "similarity": 0.45},
    ]
    captured_messages = []

    async def capture_messages(messages):
        captured_messages.extend(messages)
        return "Great!"

    mock_llm.generate_response = capture_messages
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = _neutral_ctx()
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    await RAGService().generate_response(
        db=mock_db, user_id=user_id, user_message="What music do I like?"
    )

    # The system message (first in the list) should contain the memory
    system_content = captured_messages[0]["content"]
    assert "jazz music" in system_content


# ──────────────────────────────────────────────────────────────────────────────
# Emotional context
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_emotional_context_in_response(
    mock_ei, mock_retrieval, mock_llm, mock_db, user_id
):
    from app.services.emotional_intelligence_service import Emotion, EmotionalIntensity, EmotionalContext

    stress_ctx = EmotionalContext(
        primary_emotion=Emotion.STRESS,
        confidence=0.75,
        intensity=EmotionalIntensity.HIGH,
        should_acknowledge=True,
        store_as_memory=True,
    )
    mock_retrieval.search_similar_memories.return_value = []
    mock_llm.generate_response = AsyncMock(return_value="I hear you.")
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = stress_ctx
    mock_ei.format_for_prompt.return_value = "User is stressed."

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=mock_db, user_id=user_id,
        user_message="I can't cope with all these deadlines"
    )

    ec = result["emotional_context"]
    assert ec["emotion"] == "stress"
    assert ec["intensity"] == "high"
    assert ec["confidence"] == 0.75
    assert ec["should_acknowledge"] is True

