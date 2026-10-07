from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.conversation as conversation_api
from app.api.conversation import router
from app.api.dependencies import get_current_user
from app.infrastructure.database import get_db


class FakeConversationRepository:
    """Fake conversation repository."""

    def __init__(
        self,
        conversations=None,
        conversation=None,
    ):
        self.conversations = conversations or []
        self.conversation = conversation

    def get_by_user(self, user_id):
        return self.conversations

    def get_user_conversation(
        self,
        *,
        conversation_id,
        user_id,
    ):
        return self.conversation


class FakeMessageRepository:
    """Fake message repository."""

    def __init__(self, messages=None):
        self.messages = messages or []

    def get_by_conversation(
        self,
        conversation_id,
    ):
        return self.messages


def create_client(
    *,
    conversations=None,
    conversation=None,
    messages=None,
):
    app = FastAPI()

    app.include_router(router)

    user = SimpleNamespace(
        id=uuid4(),
        is_active=True,
    )

    fake_conversation_repository = (
        FakeConversationRepository(
            conversations=conversations,
            conversation=conversation,
        )
    )

    fake_message_repository = (
        FakeMessageRepository(messages)
    )

    class FakeDB:
        pass

    def fake_db():
        yield FakeDB()

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    app.dependency_overrides[
        get_db
    ] = fake_db

    original_conversation_repository = (
        conversation_api.ConversationRepository
    )

    original_message_repository = (
        conversation_api.MessageRepository
    )

    conversation_api.ConversationRepository = (
        lambda db: fake_conversation_repository
    )

    conversation_api.MessageRepository = (
        lambda db: fake_message_repository
    )

    client = TestClient(app)

    return (
        client,
        user,
        original_conversation_repository,
        original_message_repository,
    )


def restore_repositories(
    original_conversation_repository,
    original_message_repository,
):
    conversation_api.ConversationRepository = (
        original_conversation_repository
    )

    conversation_api.MessageRepository = (
        original_message_repository
    )


def test_get_conversations_returns_user_conversations():
    """Verify conversation list endpoint."""

    conversation = SimpleNamespace(
        id=uuid4(),
        title="Leave Policy",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    (
        client,
        _,
        original_conversation_repository,
        original_message_repository,
    ) = create_client(
        conversations=[conversation]
    )

    try:
        response = client.get(
            "/conversations"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == str(
            conversation.id
        )
        assert data[0]["title"] == (
            "Leave Policy"
        )

    finally:
        restore_repositories(
            original_conversation_repository,
            original_message_repository,
        )


def test_get_conversation_returns_messages():
    """Verify conversation history endpoint."""

    conversation_id = uuid4()

    conversation = SimpleNamespace(
        id=conversation_id,
        title="Leave Policy",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    user_message = SimpleNamespace(
        id=uuid4(),
        role="user",
        content="What is the leave policy?",
        token_count=None,
        latency_ms=None,
        created_at=datetime.now(timezone.utc),
    )

    assistant_message = SimpleNamespace(
        id=uuid4(),
        role="assistant",
        content=(
            "Employees receive twenty "
            "leave days."
        ),
        token_count=None,
        latency_ms=100,
        created_at=datetime.now(timezone.utc),
    )

    (
        client,
        _,
        original_conversation_repository,
        original_message_repository,
    ) = create_client(
        conversation=conversation,
        messages=[
            user_message,
            assistant_message,
        ],
    )

    try:
        response = client.get(
            f"/conversations/{conversation_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(
            conversation_id
        )

        assert data["title"] == (
            "Leave Policy"
        )

        assert len(data["messages"]) == 2

        assert data["messages"][0]["role"] == (
            "user"
        )

        assert data["messages"][1]["role"] == (
            "assistant"
        )

        assert data["messages"][1]["latency_ms"] == 100

    finally:
        restore_repositories(
            original_conversation_repository,
            original_message_repository,
        )


def test_get_conversation_returns_404_for_missing():
    """Verify missing conversation returns 404."""

    (
        client,
        _,
        original_conversation_repository,
        original_message_repository,
    ) = create_client(
        conversation=None
    )

    try:
        response = client.get(
            f"/conversations/{uuid4()}"
        )

        assert response.status_code == 404

        assert response.json()["detail"] == (
            "Conversation not found."
        )

    finally:
        restore_repositories(
            original_conversation_repository,
            original_message_repository,
        )
