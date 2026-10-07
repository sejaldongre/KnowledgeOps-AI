from uuid import uuid4

from sqlalchemy.orm import Session

from app.infrastructure.database import engine
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User
from app.repositories.message import MessageRepository


def create_test_user(db: Session) -> User:
    """Create a valid database user."""

    user = User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="repository-test-password",
        full_name="Message Repository Test User",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_get_messages_by_conversation():
    """Verify messages are returned in creation order."""

    with Session(engine) as db:
        user = create_test_user(db)

        conversation = Conversation(
            id=uuid4(),
            user_id=user.id,
            title="Repository Test Conversation",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        first_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="What is the leave policy?",
        )

        second_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="Employees receive twenty paid leave days.",
        )

        db.add_all(
            [
                first_message,
                second_message,
            ]
        )
        db.commit()

        repository = MessageRepository(db)

        messages = repository.get_by_conversation(
            conversation.id
        )

        assert len(messages) == 2

        assert messages[0].id == first_message.id
        assert messages[0].role == MessageRole.USER
        assert messages[0].content == (
            "What is the leave policy?"
        )

        assert messages[1].id == second_message.id
        assert messages[1].role == MessageRole.ASSISTANT
        assert messages[1].content == (
            "Employees receive twenty paid leave days."
        )

        db.delete(conversation)
        db.delete(user)
        db.commit()
