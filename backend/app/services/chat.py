from dataclasses import dataclass
from time import perf_counter
from uuid import UUID

from app.core.config import Settings
from app.models.message import MessageRole
from app.repositories.conversation import (
    ConversationRepository,
)
from app.repositories.message import MessageRepository
from app.services.graph.workflow import build_rag_graph
from app.services.llm.base import LLMService
from app.services.llm.factory import (
    LLMMode,
    create_llm_service,
)
from app.services.rag import RAGPromptBuilder
from app.services.retrieval import RetrievalResult
from app.services.retrieval import RetrievalService


@dataclass
class ChatResult:
    """Result returned by the chat service."""

    conversation_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    answer: str
    sources: list[RetrievalResult]
    llm_mode: LLMMode
    latency_ms: int


class ChatService:
    """Orchestrate conversations through the RAG graph."""

    def __init__(
        self,
        *,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        retrieval_service: RetrievalService,
        prompt_builder: RAGPromptBuilder,
        settings: Settings,
        llm_service: LLMService | None = None,
    ) -> None:
        self.conversation_repository = (
            conversation_repository
        )

        self.message_repository = (
            message_repository
        )

        self.retrieval_service = (
            retrieval_service
        )

        self.prompt_builder = prompt_builder

        self.settings = settings

        self.llm_service = llm_service

    def chat(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: UUID | None = None,
        llm_mode: LLMMode | None = None,
        retrieval_limit: int = 5,
    ) -> ChatResult:
        """Process a user message through the RAG graph."""

        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError(
                "Message cannot be empty."
            )

        conversation = (
            self._get_or_create_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                message=cleaned_message,
            )
        )

        user_message = (
            self.message_repository.create(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=cleaned_message,
            )
        )

        start_time = perf_counter()

        selected_mode = (
            llm_mode
            if llm_mode is not None
            else self.settings.llm_default_mode
        )

        llm = self.llm_service

        if llm is None:
            llm = create_llm_service(
                mode=selected_mode,
                settings=self.settings,
            )

        graph = build_rag_graph(
            retrieval_service=(
                self.retrieval_service
            ),
            prompt_builder=self.prompt_builder,
            llm_service=llm,
        )

        graph_result = graph.invoke(
            {
                "user_id": user_id,
                "query": cleaned_message,
                "original_query": cleaned_message,
                "conversation_id": conversation.id,
                "retrieval_limit": retrieval_limit,
                "query_attempts": 0,
                "max_query_attempts": 2,
                "llm_mode": selected_mode,
            }
        )

        answer = graph_result["answer"]

        sources = graph_result.get(
            "retrieved_chunks",
            [],
        )

        latency_ms = int(
            (perf_counter() - start_time) * 1000
        )

        assistant_message = (
            self.message_repository.create(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=answer,
                latency_ms=latency_ms,
            )
        )

        return ChatResult(
            conversation_id=conversation.id,
            user_message_id=user_message.id,
            assistant_message_id=(
                assistant_message.id
            ),
            answer=answer,
            sources=sources,
            llm_mode=selected_mode,
            latency_ms=latency_ms,
        )

    def _get_or_create_conversation(
        self,
        *,
        user_id: UUID,
        conversation_id: UUID | None,
        message: str,
    ):
        """Get an owned conversation or create a new one."""

        if conversation_id is not None:
            conversation = (
                self.conversation_repository
                .get_user_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                )
            )

            if conversation is None:
                raise ValueError(
                    "Conversation not found."
                )

            return conversation

        title = self._create_title(message)

        return self.conversation_repository.create(
            user_id=user_id,
            title=title,
        )

    @staticmethod
    def _create_title(message: str) -> str:
        """Create a simple conversation title."""

        title = " ".join(
            message.split()
        )

        if len(title) <= 80:
            return title

        return f"{title[:77]}..."
