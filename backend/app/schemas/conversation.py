from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.message import MessageRole


class ConversationSummary(BaseModel):
    """Summary of a conversation."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """A message belonging to a conversation."""

    id: UUID
    role: MessageRole
    content: str
    token_count: int | None = None
    latency_ms: int | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """Conversation with its message history."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]
