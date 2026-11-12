
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    user_id: UUID
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    retrieved_memories: list[dict]
    memory_count: int
    model: str

    model_config = ConfigDict(from_attributes=True)
