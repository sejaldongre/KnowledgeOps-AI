from typing import Literal

from app.core.config import Settings
from app.services.llm.base import LLMService
from app.services.llm.offline import (
    OfflineLLMService,
)
from app.services.llm.online import (
    OnlineLLMService,
)


LLMMode = Literal[
    "online",
    "offline",
]


def create_llm_service(
    *,
    mode: LLMMode,
    settings: Settings,
) -> LLMService:
    """Create an LLM service for the requested mode."""

    if mode == "online":
        return OnlineLLMService(settings)

    if mode == "offline":
        return OfflineLLMService(settings)

    raise ValueError(
        f"Unsupported LLM mode: {mode}"
    )
