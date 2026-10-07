from uuid import uuid4

from app.models.conversation import Conversation
from app.repositories.conversation import (
    ConversationRepository,
)


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


def test_create_conversation():
    """Verify conversation creation."""

    db = FakeSession()

    repository = ConversationRepository(db)

    user_id = uuid4()

    result = repository.create(
        user_id=user_id,
        title="Employee Handbook",
    )

    assert isinstance(
        result,
        Conversation,
    )

    assert result.user_id == user_id
    assert result.title == "Employee Handbook"

    assert result in db.added
    assert db.committed is True
    assert result in db.refreshed
