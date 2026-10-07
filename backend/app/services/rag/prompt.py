from collections.abc import Sequence

from app.services.retrieval import RetrievalResult


class RAGPromptBuilder:
    """Build prompts using retrieved document context."""

    SYSTEM_INSTRUCTION = """You are KnowledgeOps AI,
an enterprise knowledge assistant.

Answer the user's question using only the provided
knowledge context.

Rules:
1. Use the provided knowledge context as the primary
   source of truth.
2. Do not invent facts that are not supported by the
   knowledge context.
3. If the context does not contain enough information
   to answer the question, clearly say that the
   information was not found in the available
   documents.
4. Give a concise and useful answer.
5. When possible, mention which source document
   supports the answer.
"""

    def build(
        self,
        *,
        query: str,
        results: Sequence[RetrievalResult],
    ) -> str:
        """Build a RAG prompt from a query and results."""

        context = self._build_context(results)

        return (
            f"{self.SYSTEM_INSTRUCTION}\n\n"
            "KNOWLEDGE CONTEXT:\n"
            f"{context}\n\n"
            "USER QUESTION:\n"
            f"{query.strip()}\n\n"
            "ANSWER:"
        )

    def _build_context(
        self,
        results: Sequence[RetrievalResult],
    ) -> str:
        """Format retrieved chunks as prompt context."""

        if not results:
            return (
                "No relevant information was found "
                "in the available documents."
            )

        sections: list[str] = []

        for index, result in enumerate(results, start=1):
            sections.append(
                (
                    f"[Source {index}]\n"
                    f"Document ID: {result.document_id}\n"
                    f"Document Version ID: "
                    f"{result.document_version_id}\n"
                    f"Chunk Index: {result.chunk_index}\n"
                    f"Content:\n{result.text}"
                )
            )

        return "\n\n".join(sections)
