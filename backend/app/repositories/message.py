from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(
    BaseRepository[Message]
):
    """Repository for message persistence."""

    def __init__(self, db: Session) -> None:
        super().__init__(Message, db)

    def create(
        self,
        *,
        conversation_id: UUID,
        role,
        content: str,
        token_count: int | None = None,
        latency_ms: int | None = None,
    ) -> Message:
        """Create a message in a conversation."""

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            latency_ms=latency_ms,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        """Return messages belonging to a conversation."""

        statement = (
            select(Message)
            .where(
                Message.conversation_id
                == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )
