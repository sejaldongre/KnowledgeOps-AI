from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(
    BaseRepository[Conversation]
):
    """Repository for conversation persistence."""

    def __init__(self, db: Session) -> None:
        super().__init__(Conversation, db)

    def create(
        self,
        *,
        user_id: UUID,
        title: str,
    ) -> Conversation:
        """Create a new conversation."""

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_by_id(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        """Return a conversation by ID."""

        statement = select(Conversation).where(
            Conversation.id == conversation_id
        )

        return self.db.scalar(statement)

    def get_by_user(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        """Return conversations belonging to a user."""

        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.updated_at.desc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_user_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        """Return a conversation only if it belongs to the user."""

        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )

        return self.db.scalar(statement)
