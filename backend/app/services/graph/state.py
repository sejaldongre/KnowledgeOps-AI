from typing import TypedDict
from uuid import UUID

from app.services.retrieval import RetrievalResult


class RAGGraphState(TypedDict, total=False):
    """State carried through the LangGraph RAG workflow."""

    user_id: UUID
    query: str
    original_query: str
    conversation_id: UUID | None

    retrieval_limit: int

    retrieved_chunks: list[RetrievalResult]

    query_attempts: int
    max_query_attempts: int

    prompt: str
    answer: str

    llm_mode: str

    error: str | None
