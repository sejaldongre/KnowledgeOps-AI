from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_chat_service,
    get_current_user,
)
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSource,
)
from app.services.chat import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    data: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    chat_service: ChatService = Depends(
        get_chat_service
    ),
) -> ChatResponse:
    """Send a message through the RAG chat workflow."""

    result = chat_service.chat(
        user_id=current_user.id,
        message=data.message,
        conversation_id=data.conversation_id,
        llm_mode=data.llm_mode,
        retrieval_limit=data.retrieval_limit,
    )

    return ChatResponse(
        conversation_id=result.conversation_id,
        user_message_id=result.user_message_id,
        assistant_message_id=(
            result.assistant_message_id
        ),
        answer=result.answer,
        sources=[
            ChatSource(
                chunk_id=source.chunk_id,
                document_id=source.document_id,
                document_version_id=(
                    source.document_version_id
                ),
                chunk_index=source.chunk_index,
                text=source.text,
                distance=source.distance,
            )
            for source in result.sources
        ],
        llm_mode=result.llm_mode,
        latency_ms=result.latency_ms,
    )
