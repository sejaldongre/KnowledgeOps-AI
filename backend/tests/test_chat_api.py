from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.chat import router
from app.api.dependencies import (
    get_chat_service,
    get_current_user,
)
from app.services.chat import ChatResult


class FakeChatService:
    """Fake chat service for API tests."""

    def __init__(self):
        self.called_with = None

    def chat(
        self,
        *,
        user_id,
        message,
        conversation_id=None,
        llm_mode=None,
        retrieval_limit=5,
    ):
        self.called_with = {
            "user_id": user_id,
            "message": message,
            "conversation_id": conversation_id,
            "llm_mode": llm_mode,
            "retrieval_limit": retrieval_limit,
        }

        return ChatResult(
            conversation_id=(
                conversation_id
                or uuid4()
            ),
            user_message_id=uuid4(),
            assistant_message_id=uuid4(),
            answer=(
                "Employees receive twenty "
                "leave days."
            ),
            sources=[],
            llm_mode=(
                llm_mode
                or "offline"
            ),
            latency_ms=42,
        )


def create_client():
    """Create a test FastAPI client."""

    app = FastAPI()

    app.include_router(router)

    fake_service = FakeChatService()

    user = SimpleNamespace(
        id=uuid4(),
        is_active=True,
    )

    app.dependency_overrides[
        get_current_user
    ] = lambda: user

    app.dependency_overrides[
        get_chat_service
    ] = lambda: fake_service

    return (
        TestClient(app),
        fake_service,
        user,
    )


def test_chat_endpoint_returns_response():
    """Verify the chat endpoint returns a valid response."""

    client, _, _ = create_client()

    response = client.post(
        "/chat",
        json={
            "message": "What is the leave policy?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["answer"]
        == "Employees receive twenty leave days."
    )

    assert data["llm_mode"] == "offline"

    assert data["latency_ms"] == 42

    assert "conversation_id" in data
    assert "user_message_id" in data
    assert "assistant_message_id" in data

    assert data["sources"] == []


def test_chat_endpoint_passes_llm_mode():
    """Verify selected LLM mode reaches ChatService."""

    client, fake_service, user = (
        create_client()
    )

    conversation_id = uuid4()

    response = client.post(
        "/chat",
        json={
            "message": "Explain the policy.",
            "conversation_id": str(
                conversation_id
            ),
            "llm_mode": "online",
            "retrieval_limit": 10,
        },
    )

    assert response.status_code == 200

    assert fake_service.called_with == {
        "user_id": user.id,
        "message": "Explain the policy.",
        "conversation_id": conversation_id,
        "llm_mode": "online",
        "retrieval_limit": 10,
    }


def test_chat_endpoint_rejects_empty_message():
    """Verify empty messages are rejected."""

    client, _, _ = create_client()

    response = client.post(
        "/chat",
        json={
            "message": "",
        },
    )

    assert response.status_code == 422
