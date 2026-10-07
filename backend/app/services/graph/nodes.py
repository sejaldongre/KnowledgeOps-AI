from app.services.graph.state import RAGGraphState
from app.services.llm.base import LLMService
from app.services.rag import RAGPromptBuilder
from app.services.retrieval import RetrievalService


class RAGGraphNodes:
    """Nodes used by the LangGraph RAG workflow."""

    def __init__(
        self,
        *,
        retrieval_service: RetrievalService,
        prompt_builder: RAGPromptBuilder,
        llm_service: LLMService,
    ) -> None:
        self.retrieval_service = (
            retrieval_service
        )
        self.prompt_builder = (
            prompt_builder
        )
        self.llm_service = llm_service

    def retrieve(
        self,
        state: RAGGraphState,
    ) -> dict:
        """Retrieve permission-aware document chunks."""

        attempts = state.get(
            "query_attempts",
            0,
        )

        results = self.retrieval_service.search(
            query=state["query"],
            user_id=state["user_id"],
            limit=state.get(
                "retrieval_limit",
                5,
            ),
        )

        return {
            "retrieved_chunks": results,
            "query_attempts": attempts + 1,
        }

    def refine_query(
        self,
        state: RAGGraphState,
    ) -> dict:
        """Perform deterministic query refinement."""

        query = state["query"].strip()

        refined_query = (
            f"{query} relevant policy documentation"
        )

        return {
            "query": refined_query,
        }

    def build_prompt(
        self,
        state: RAGGraphState,
    ) -> dict:
        """Build the RAG prompt from retrieved context."""

        prompt = self.prompt_builder.build(
            query=state["query"],
            results=state.get(
                "retrieved_chunks",
                [],
            ),
        )

        return {
            "prompt": prompt,
        }

    def generate(
        self,
        state: RAGGraphState,
    ) -> dict:
        """Generate the final answer with the selected LLM."""

        answer = self.llm_service.generate(
            prompt=state["prompt"],
        )

        return {
            "answer": answer,
        }

    def no_context(
        self,
        state: RAGGraphState,
    ) -> dict:
        """Return a safe response when no context is available."""

        return {
            "answer": (
                "I could not find relevant information "
                "in the available knowledge base to answer "
                "your question."
            )
        }
