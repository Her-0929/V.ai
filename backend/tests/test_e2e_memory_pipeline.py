"""
End-to-end memory pipeline test.

Scenario (from the master spec):
  1. User says: "I want to become an AI engineer."
  2. HER extracts and stores this career goal.
  3. User ends the conversation.
  4. A new conversation starts.
  5. User asks: "What career goal did I previously share?"
  6. HER retrieves the correct memory.
  7. HER provides a direct personalized answer.

All external services (LLM, DB, embeddings) are mocked.
This test verifies the complete data flow — not just database presence.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, call
from uuid import uuid4

from app.services.emotional_intelligence_service import (
    Emotion, EmotionalIntensity, EmotionalContext,
)

USER_ID = uuid4()

_MOCK_EMBEDDING = [0.1] * 384

_CAREER_GOAL_MEMORY = {
    "id": str(uuid4()),
    "content": "User wants to become an AI engineer",
    "memory_type": "career_goal",
    "importance": 5,
    "confidence": 0.95,
    "similarity": 0.27,   # matches real observed range: 0.23–0.27
}


# ──────────────────────────────────────────────────────────────────────────────
# Step 1–2: Extraction stores the career goal
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.memory_service.embedding_service")
@patch("app.services.memory_extraction_service.llm_service")
async def test_step1_extraction_calls_create_memory(mock_llm, mock_emb):
    """The extraction service should call create_memory with memory_type='career_goal'."""
    from app.services.memory_extraction_service import MemoryExtractionService
    from app.services.memory_service import MemoryService
    from app.models.memory import Memory

    mock_emb.generate_embedding.return_value = _MOCK_EMBEDDING

    # LLM returns a valid career_goal extraction
    mock_llm.generate_response = AsyncMock(return_value=(
        '{"content": "User wants to become an AI engineer", '
        '"memory_type": "career_goal", "importance": 5, '
        '"confidence": 0.95, "excerpt": "I want to become an AI engineer"}'
    ))

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    # Capture what create_memory is called with
    created_calls = []

    def fake_create_memory(**kwargs):
        created_calls.append(kwargs)
        mem = MagicMock(spec=Memory)
        mem.content = kwargs["content"]
        mem.memory_type = kwargs["memory_type"]
        mem.importance = kwargs["importance"]
        return mem

    with patch.object(MemoryService, "find_duplicate", return_value=None), \
         patch.object(MemoryService, "create_memory", side_effect=fake_create_memory):

        svc = MemoryExtractionService()
        result = await svc.extract_from_message_pair(
            db=mock_db,
            user_id=USER_ID,
            user_message="I want to become an AI engineer.",
            assistant_response="That's a great goal! Being an AI engineer is very rewarding.",
        )

    # Verify create_memory was called
    assert len(created_calls) == 1
    assert created_calls[0]["memory_type"] == "career_goal"
    assert "AI engineer" in created_calls[0]["content"]
    assert created_calls[0]["importance"] == 5
    assert created_calls[0]["user_id"] == USER_ID


@pytest.mark.asyncio
@patch("app.services.memory_service.embedding_service")
@patch("app.services.memory_extraction_service.llm_service")
async def test_step2_no_extraction_for_no_memories(mock_llm, mock_emb):
    """When LLM says NO_MEMORIES, no memories should be created."""
    from app.services.memory_extraction_service import MemoryExtractionService
    from app.services.memory_service import MemoryService

    mock_emb.generate_embedding.return_value = _MOCK_EMBEDDING
    mock_llm.generate_response = AsyncMock(return_value="NO_MEMORIES")

    mock_db = MagicMock()

    with patch.object(MemoryService, "find_duplicate", return_value=None), \
         patch.object(MemoryService, "create_memory") as mock_create:

        svc = MemoryExtractionService()
        result = await svc.extract_from_message_pair(
            db=mock_db,
            user_id=USER_ID,
            user_message="Hello, how are you?",
            assistant_response="I'm doing well, thanks!",
        )

    mock_create.assert_not_called()
    assert result == []


# ──────────────────────────────────────────────────────────────────────────────
# Step 3: Duplicate detection skips re-creation
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.memory_service.embedding_service")
@patch("app.services.memory_extraction_service.llm_service")
async def test_step3_duplicate_not_re_created(mock_llm, mock_emb):
    """If the same memory already exists (similarity ≥ 0.90), don't create a duplicate."""
    from app.services.memory_extraction_service import MemoryExtractionService
    from app.services.memory_service import MemoryService
    from app.models.memory import Memory

    mock_emb.generate_embedding.return_value = _MOCK_EMBEDDING
    mock_llm.generate_response = AsyncMock(return_value=(
        '{"content": "User wants to become an AI engineer", '
        '"memory_type": "career_goal", "importance": 5, '
        '"confidence": 0.95, "excerpt": "I want to become an AI engineer"}'
    ))

    mock_db = MagicMock()

    # Simulate an existing duplicate memory
    existing = MagicMock(spec=Memory)
    existing.importance = 4
    existing.confidence = 0.90

    with patch.object(MemoryService, "find_duplicate", return_value=existing), \
         patch.object(MemoryService, "create_memory") as mock_create, \
         patch.object(MemoryService, "update_memory") as mock_update:

        svc = MemoryExtractionService()
        await svc.extract_from_message_pair(
            db=mock_db,
            user_id=USER_ID,
            user_message="I want to become an AI engineer.",
            assistant_response="That's great!",
        )

    # Should NOT create a new memory
    mock_create.assert_not_called()


# ──────────────────────────────────────────────────────────────────────────────
# Steps 4–7: New conversation retrieves and uses the memory
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_step4_memory_retrieved_in_new_conversation(
    mock_ei, mock_retrieval, mock_llm
):
    """In a new conversation, the career goal is retrieved with realistic similarity."""
    # Simulate the stored memory being returned by vector search
    mock_retrieval.search_similar_memories.return_value = [_CAREER_GOAL_MEMORY]

    mock_llm.generate_response = AsyncMock(
        return_value="You previously shared a career goal to become an AI engineer."
    )
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=MagicMock(),
        user_id=USER_ID,
        user_message="What career goal did I previously share?",
    )

    # Verify memory was retrieved
    assert result["memory_count"] == 1
    assert result["retrieved_memories"][0]["memory_type"] == "career_goal"
    assert "AI engineer" in result["retrieved_memories"][0]["content"]
    assert result["retrieved_memories"][0]["similarity"] == 0.27


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_step5_memory_injected_into_llm_context(
    mock_ei, mock_retrieval, mock_llm
):
    """The memory content must appear in the system prompt sent to the LLM."""
    mock_retrieval.search_similar_memories.return_value = [_CAREER_GOAL_MEMORY]

    captured = []

    async def capture(messages):
        captured.extend(messages)
        return "You shared a goal to become an AI engineer."

    mock_llm.generate_response = capture
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    await RAGService().generate_response(
        db=MagicMock(),
        user_id=USER_ID,
        user_message="What career goal did I previously share?",
    )

    # System message must contain the memory
    assert len(captured) >= 2
    system_message = captured[0]["content"]
    assert captured[0]["role"] == "system"
    assert "AI engineer" in system_message


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_step6_response_references_career_goal(
    mock_ei, mock_retrieval, mock_llm
):
    """The final response should reference the career goal."""
    mock_retrieval.search_similar_memories.return_value = [_CAREER_GOAL_MEMORY]
    mock_llm.generate_response = AsyncMock(
        return_value="You previously shared a career goal to become an AI engineer."
    )
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=MagicMock(),
        user_id=USER_ID,
        user_message="What career goal did I previously share?",
    )

    assert "AI engineer" in result["response"]


@pytest.mark.asyncio
@patch("app.services.rag_service.llm_service")
@patch("app.services.rag_service.memory_retrieval_service")
@patch("app.services.rag_service.emotional_intelligence_service")
async def test_step7_below_threshold_memory_not_used(
    mock_ei, mock_retrieval, mock_llm
):
    """A memory with similarity below 0.20 must NOT be injected into the prompt."""
    low_sim = {**_CAREER_GOAL_MEMORY, "similarity": 0.08}
    mock_retrieval.search_similar_memories.return_value = [low_sim]

    captured = []

    async def capture(messages):
        captured.extend(messages)
        return "I don't have that information."

    mock_llm.generate_response = capture
    mock_llm.model = "qwen3:1.7b"
    mock_ei.analyze_message.return_value = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    mock_ei.format_for_prompt.return_value = ""

    from app.services.rag_service import RAGService
    result = await RAGService().generate_response(
        db=MagicMock(),
        user_id=USER_ID,
        user_message="What career goal did I previously share?",
    )

    assert result["memory_count"] == 0
    system_message = captured[0]["content"]
    assert "AI engineer" not in system_message

