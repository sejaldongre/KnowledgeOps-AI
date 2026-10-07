import httpx

from app.core.config import Settings
from app.services.llm.base import LLMService


class OnlineLLMService(LLMService):
    """Online LLM service using a Groq-compatible API."""

    def __init__(
        self,
        settings: Settings,
        timeout: float = 60.0,
    ) -> None:
        self.settings = settings
        self.timeout = timeout

    def generate(
        self,
        *,
        prompt: str,
    ) -> str:
        """Generate a response using the online LLM."""

        if not self.settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        if not self.settings.groq_model:
            raise RuntimeError(
                "GROQ_MODEL is not configured."
            )

        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        headers = {
            "Authorization": (
                f"Bearer {self.settings.groq_api_key}"
            ),
            "Content-Type": "application/json",
        }

        with httpx.Client(
            timeout=self.timeout
        ) as client:
            response = client.post(
                self.settings.groq_api_url,
                json=payload,
                headers=headers,
            )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
