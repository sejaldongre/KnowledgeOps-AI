from uuid import uuid4

from app.models.message import Message, MessageRole
from app.repositories.message import MessageRepository


class FakeSession:
    """Fake session for repository unit tests."""

    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def refresh(self, value):
        self.refreshed.append(value)


def test_create_message():
    """Verify message creation."""

    db = FakeSession()

    repository = MessageRepository(db)

    conversation_id = uuid4()

    result = repository.create(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content="What is the leave policy?",
    )

    assert isinstance(result, Message)

    assert result.conversation_id == conversation_id
    assert result.role == MessageRole.USER
    assert result.content == (
        "What is the leave policy?"
    )
    assert result.token_count is None
    assert result.latency_ms is None

    assert result in db.added
    assert db.committed is True
    assert result in db.refreshed


def test_create_message_with_metadata():
    """Verify optional message metadata is persisted."""

    db = FakeSession()

    repository = MessageRepository(db)

    conversation_id = uuid4()

    result = repository.create(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content="Employees receive twenty paid leave days.",
        token_count=12,
        latency_ms=350,
    )

    assert result.conversation_id == conversation_id
    assert result.role == MessageRole.ASSISTANT
    assert result.content == (
        "Employees receive twenty paid leave days."
    )
    assert result.token_count == 12
    assert result.latency_ms == 350

    assert result in db.added
    assert db.committed is True
    assert result in db.refreshed
