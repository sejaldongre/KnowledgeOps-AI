from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.chat import ChatService
from app.services.retrieval import RetrievalResult


class FakeConversationRepository:
    """Fake conversation repository."""

    def __init__(self):
        self.created = []
        self.existing = {}

    def create(self, *, user_id, title):
        conversation = SimpleNamespace(
            id=uuid4(),
            user_id=user_id,
            title=title,
        )

        self.created.append(
            {
                "user_id": user_id,
                "title": title,
            }
        )

        return conversation

    def get_user_conversation(
        self,
        *,
        conversation_id,
        user_id,
    ):
        return self.existing.get(
            (conversation_id, user_id)
        )


class FakeMessageRepository:
    """Fake message repository."""

    def __init__(self):
        self.created = []

    def create(
        self,
        *,
        conversation_id,
        role,
        content,
        token_count=None,
        latency_ms=None,
    ):
        message = SimpleNamespace(
            id=uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            latency_ms=latency_ms,
        )

        self.created.append(message)

        return message


class FakeRetrievalService:
    """Fake retrieval service."""

    def __init__(self, results):
        self.results = results
        self.called_with = None

    def search(
        self,
        *,
        query,
        user_id,
        limit,
    ):
        self.called_with = {
            "query": query,
            "user_id": user_id,
            "limit": limit,
        }

        return self.results


class FakePromptBuilder:
    """Fake RAG prompt builder."""

    def __init__(self):
        self.called_with = None

    def build(
        self,
        *,
        query,
        results,
    ):
        self.called_with = {
            "query": query,
            "results": results,
        }

        return f"PROMPT: {query}"


class FakeLLMService:
    """Fake LLM service."""

    def __init__(self, answer="Generated answer"):
        self.answer = answer
        self.called_with = None

    def generate(self, *, prompt):
        self.called_with = {
            "prompt": prompt,
        }

        return self.answer


class FakeSettings:
    """Fake settings for chat tests."""

    llm_default_mode = "offline"


def create_service(
    *,
    results=None,
    llm=None,
):
    conversation_repository = (
        FakeConversationRepository()
    )

    message_repository = (
        FakeMessageRepository()
    )

    if results is None:
        document_id = uuid4()
        version_id = uuid4()

        results = [
            RetrievalResult(
                chunk_id=str(uuid4()),
                document_id=document_id,
                document_version_id=version_id,
                chunk_index=0,
                text="Employees receive twenty paid leave days.",
                distance=0.12,
            )
        ]

    retrieval_service = FakeRetrievalService(
        results
    )

    prompt_builder = FakePromptBuilder()

    service = ChatService(
        conversation_repository=(
            conversation_repository
        ),
        message_repository=(
            message_repository
        ),
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        settings=FakeSettings(),
        llm_service=llm or FakeLLMService(),
    )

    return (
        service,
        conversation_repository,
        message_repository,
        retrieval_service,
        prompt_builder,
    )


def test_chat_creates_conversation_and_messages():
    """Verify a new conversation is created."""

    user_id = uuid4()

    llm = FakeLLMService(
        "Employees receive twenty leave days."
    )

    (
        service,
        conversation_repository,
        message_repository,
        _,
        _,
    ) = create_service(llm=llm)

    result = service.chat(
        user_id=user_id,
        message="What is the leave policy?",
    )

    assert result.answer == (
        "Employees receive twenty leave days."
    )

    assert len(
        conversation_repository.created
    ) == 1

    assert len(
        message_repository.created
    ) == 2


def test_chat_saves_user_and_assistant_messages():
    """Verify both sides of the conversation are saved."""

    llm = FakeLLMService(
        "The answer is available."
    )

    (
        service,
        _,
        message_repository,
        _,
        _,
    ) = create_service(llm=llm)

    result = service.chat(
        user_id=uuid4(),
        message="Tell me about the policy.",
    )

    user_message = (
        message_repository.created[0]
    )

    assistant_message = (
        message_repository.created[1]
    )

    assert user_message.role.value == "user"
    assert (
        user_message.content
        == "Tell me about the policy."
    )

    assert (
        assistant_message.role.value
        == "assistant"
    )

    assert (
        assistant_message.content
        == "The answer is available."
    )

    assert (
        result.user_message_id
        == user_message.id
    )

    assert (
        result.assistant_message_id
        == assistant_message.id
    )


def test_chat_retrieves_and_builds_prompt():
    """Verify retrieval results reach the prompt builder."""

    document_id = uuid4()
    version_id = uuid4()

    result = RetrievalResult(
        chunk_id=str(uuid4()),
        document_id=document_id,
        document_version_id=version_id,
        chunk_index=0,
        text="Twenty paid leave days.",
        distance=0.12,
    )

    llm = FakeLLMService()

    (
        service,
        _,
        _,
        retrieval_service,
        prompt_builder,
    ) = create_service(
        results=[result],
        llm=llm,
    )

    service.chat(
        user_id=uuid4(),
        message="How many leave days?",
        retrieval_limit=7,
    )

    assert retrieval_service.called_with[
        "query"
    ] == "How many leave days?"

    assert retrieval_service.called_with[
        "limit"
    ] == 7

    assert prompt_builder.called_with[
        "results"
    ] == [result]

    assert (
        llm.called_with["prompt"]
        == "PROMPT: How many leave days?"
    )


def test_chat_uses_requested_llm_mode():
    """Verify the requested mode is returned."""

    (
        service,
        _,
        _,
        _,
        _,
    ) = create_service(
        llm=FakeLLMService()
    )

    result = service.chat(
        user_id=uuid4(),
        message="What is the policy?",
        llm_mode="online",
    )

    assert result.llm_mode == "online"


def test_chat_uses_default_llm_mode():
    """Verify default mode is used when none is supplied."""

    (
        service,
        _,
        _,
        _,
        _,
    ) = create_service(
        llm=FakeLLMService()
    )

    result = service.chat(
        user_id=uuid4(),
        message="What is the policy?",
    )

    assert result.llm_mode == "offline"


def test_chat_reuses_owned_conversation():
    """Verify an existing owned conversation is reused."""

    user_id = uuid4()
    conversation_id = uuid4()

    (
        service,
        conversation_repository,
        message_repository,
        _,
        _,
    ) = create_service(
        llm=FakeLLMService()
    )

    existing = SimpleNamespace(
        id=conversation_id,
        user_id=user_id,
        title="Existing conversation",
    )

    conversation_repository.existing[
        (conversation_id, user_id)
    ] = existing

    result = service.chat(
        user_id=user_id,
        conversation_id=conversation_id,
        message="Continue our discussion.",
    )

    assert (
        result.conversation_id
        == conversation_id
    )

    assert (
        conversation_repository.created
        == []
    )

    assert (
        len(message_repository.created)
        == 2
    )


def test_chat_rejects_unknown_conversation():
    """Verify another or missing conversation is rejected."""

    service, _, _, _, _ = create_service(
        llm=FakeLLMService()
    )

    with pytest.raises(ValueError):
        service.chat(
            user_id=uuid4(),
            conversation_id=uuid4(),
            message="Hello",
        )


def test_chat_rejects_blank_message():
    """Verify blank messages are rejected."""

    service, _, _, _, _ = create_service(
        llm=FakeLLMService()
    )

    with pytest.raises(ValueError):
        service.chat(
            user_id=uuid4(),
            message="   ",
        )
