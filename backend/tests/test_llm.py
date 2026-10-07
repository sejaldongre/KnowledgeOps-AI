import pytest

from app.services.llm.base import LLMService
from app.services.llm.factory import (
    create_llm_service,
)
from app.services.llm.offline import (
    OfflineLLMService,
)
from app.services.llm.online import (
    OnlineLLMService,
)


class FakeSettings:
    """Fake settings for LLM tests."""

    groq_api_key = "test-key"
    groq_api_url = (
        "https://example.com/chat"
    )
    groq_model = "test-online-model"

    ollama_base_url = (
        "http://localhost:11434"
    )
    ollama_model = "test-offline-model"


def test_online_llm_implements_interface():
    """Verify online LLM uses the common interface."""

    service = OnlineLLMService(
        FakeSettings()
    )

    assert isinstance(
        service,
        LLMService,
    )


def test_offline_llm_implements_interface():
    """Verify offline LLM uses the common interface."""

    service = OfflineLLMService(
        FakeSettings()
    )

    assert isinstance(
        service,
        LLMService,
    )


def test_factory_creates_online_service():
    """Verify online mode creates the online service."""

    service = create_llm_service(
        mode="online",
        settings=FakeSettings(),
    )

    assert isinstance(
        service,
        OnlineLLMService,
    )


def test_factory_creates_offline_service():
    """Verify offline mode creates the offline service."""

    service = create_llm_service(
        mode="offline",
        settings=FakeSettings(),
    )

    assert isinstance(
        service,
        OfflineLLMService,
    )


def test_factory_rejects_invalid_mode():
    """Verify unsupported LLM modes are rejected."""

    with pytest.raises(ValueError):
        create_llm_service(
            mode="invalid",
            settings=FakeSettings(),
        )
