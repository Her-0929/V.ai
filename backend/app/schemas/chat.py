"""HER AI — Chat API Schemas"""

from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    user_id: UUID | None = None
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=10000)



class EmotionalContextResponse(BaseModel):
    emotion: str
    intensity: str
    confidence: float
    should_acknowledge: bool


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    retrieved_memories: list[dict]
    memory_count: int
    model: str
    emotional_context: EmotionalContextResponse | None = None

    model_config = ConfigDict(from_attributes=True)
