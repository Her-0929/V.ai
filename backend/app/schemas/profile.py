from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)

class PreferenceUpdate(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: dict

class PreferenceResponse(BaseModel):
    id: UUID
    key: str
    value: dict
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProfileResponse(BaseModel):
    user: UserResponse
    preferences: list[PreferenceResponse]
    memory_count: int
    conversation_count: int

class PrivacyExportResponse(BaseModel):
    user: UserResponse
    preferences: list[PreferenceResponse]
    memories: list[dict]
    total_memories: int
    exported_at: datetime

class AccountDeleteResponse(BaseModel):
    deleted: bool
    memories_deleted: int
    message: str
