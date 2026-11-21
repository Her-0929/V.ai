"""HER AI — Conversation Schemas"""

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class ConversationStatsResponse(BaseModel):
    id: UUID
    title: str | None
    message_count: int
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]
    total_messages: int


class TitleGenerateResponse(BaseModel):
    conversation_id: UUID
    title: str


class SummaryResponse(BaseModel):
    conversation_id: UUID
    summary: str

