from abc import ABC, abstractmethod


class LLMService(ABC):
    """Abstract interface for language model providers."""

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
    ) -> str:
        """Generate a response from the supplied prompt."""

        raise NotImplementedError
