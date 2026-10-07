import httpx

from app.core.config import Settings
from app.services.llm.base import LLMService


class OfflineLLMService(LLMService):
    """Local LLM service using Ollama."""

    def __init__(
        self,
        settings: Settings,
        timeout: float = 120.0,
    ) -> None:
        self.settings = settings
        self.timeout = timeout

        # Reuse one HTTP client instead of creating a new
        # connection for every LLM request.
        self.client = httpx.Client(
            timeout=self.timeout
        )

    def generate(
        self,
        *,
        prompt: str,
    ) -> str:
        """Generate a response using the local LLM."""

        if not self.settings.offline_llm_model:
            raise RuntimeError(
                "OFFLINE_LLM_MODEL is not configured."
            )

        url = (
            f"{self.settings.ollama_base_url.rstrip('/')}"
            "/api/generate"
        )

        payload = {
            "model": self.settings.offline_llm_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Keep answers concise for a RAG knowledge assistant.
                "temperature": 0.2,
                "num_predict": 256,
            },
        }

        response = self.client.post(
            url,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response")

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return answer.strip()
