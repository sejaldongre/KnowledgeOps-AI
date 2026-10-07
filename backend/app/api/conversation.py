from fastapi import APIRouter, Depends
from fastapi import HTTPException

from app.api.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.models.user import User
from app.repositories.conversation import (
    ConversationRepository,
)
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
)
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=list[ConversationSummary],
)
def get_conversations(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> list[ConversationSummary]:
    """Return conversations belonging to the current user."""

    repository = ConversationRepository(db)

    conversations = repository.get_by_user(
        current_user.id
    )

    return [
        ConversationSummary(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        for conversation in conversations
    ]


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Return a conversation and its messages."""

    conversation_repository = (
        ConversationRepository(db)
    )

    conversation = (
        conversation_repository.get_user_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    message_repository = MessageRepository(db)

    messages = (
        message_repository.get_by_conversation(
            conversation.id
        )
    )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                token_count=message.token_count,
                latency_ms=message.latency_ms,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )
