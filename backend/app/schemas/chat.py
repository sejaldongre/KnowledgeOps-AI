from uuid import UUID

from pydantic import BaseModel, Field

from app.services.llm.factory import LLMMode


class ChatRequest(BaseModel):
    """Request body for sending a chat message."""

    message: str = Field(
        min_length=1,
        description="User message.",
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID.",
    )

    llm_mode: LLMMode | None = Field(
        default=None,
        description="LLM mode: online or offline.",
    )

    retrieval_limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of retrieved chunks.",
    )


class ChatSource(BaseModel):
    """Source document chunk used to generate the answer."""

    chunk_id: str
    document_id: UUID
    document_version_id: UUID
    chunk_index: int
    text: str
    distance: float | None = None


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    conversation_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID

    answer: str

    sources: list[ChatSource]

    llm_mode: LLMMode

    latency_ms: int
