from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    label: str
    document_id: str
    filename: str
    page: int
    chunk_id: str
    score: float
    preview: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: UUID | None = None
    document_ids: list[UUID] | None = None
    top_k: int = Field(default=5, ge=1, le=15)
    hybrid: bool = True


class MessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    citations: list[Citation] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionRead(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    sessions: list[ChatSessionRead]


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str
    citations: list[Citation]
