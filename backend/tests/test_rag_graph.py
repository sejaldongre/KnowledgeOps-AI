from uuid import uuid4

from app.services.graph.workflow import build_rag_graph
from app.services.retrieval import RetrievalResult


class FakeRetrievalService:
    """Fake retrieval service for graph tests."""

    def __init__(self, results_by_query):
        self.results_by_query = results_by_query
        self.calls = []

    def search(
        self,
        *,
        query,
        user_id,
        limit,
    ):
        self.calls.append(
            {
                "query": query,
                "user_id": user_id,
                "limit": limit,
            }
        )

        return self.results_by_query.get(
            query,
            [],
        )


class FakePromptBuilder:
    """Fake prompt builder for graph tests."""

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
    """Fake LLM service for graph tests."""

    def __init__(self):
        self.called_with = None

    def generate(
        self,
        *,
        prompt,
    ):
        self.called_with = {
            "prompt": prompt,
        }

        return "Generated answer."


def create_chunk():
    """Create a fake retrieval result."""

    return RetrievalResult(
        chunk_id="chunk-1",
        document_id=uuid4(),
        document_version_id=uuid4(),
        chunk_index=0,
        text="Employees receive twenty paid leave days.",
        distance=0.12,
    )


def test_rag_graph_runs_complete_workflow():
    """Verify normal retrieval goes directly to generation."""

    query = "What is the leave policy?"

    retrieval_service = FakeRetrievalService(
        {
            query: [create_chunk()],
        }
    )

    prompt_builder = FakePromptBuilder()
    llm_service = FakeLLMService()

    graph = build_rag_graph(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    user_id = uuid4()

    result = graph.invoke(
        {
            "user_id": user_id,
            "query": query,
            "original_query": query,
            "retrieval_limit": 5,
            "query_attempts": 0,
            "max_query_attempts": 2,
        }
    )

    assert result["query"] == query

    assert len(
        result["retrieved_chunks"]
    ) == 1

    assert result["query_attempts"] == 1

    assert result["prompt"] == (
        f"PROMPT: {query}"
    )

    assert result["answer"] == (
        "Generated answer."
    )

    assert len(
        retrieval_service.calls
    ) == 1


def test_rag_graph_refines_query_when_no_results():
    """Verify empty retrieval triggers one refinement."""

    original_query = "leave benefits"

    refined_query = (
        "leave benefits relevant policy documentation"
    )

    chunk = create_chunk()

    retrieval_service = FakeRetrievalService(
        {
            original_query: [],
            refined_query: [chunk],
        }
    )

    prompt_builder = FakePromptBuilder()
    llm_service = FakeLLMService()

    graph = build_rag_graph(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    result = graph.invoke(
        {
            "user_id": uuid4(),
            "query": original_query,
            "original_query": original_query,
            "retrieval_limit": 5,
            "query_attempts": 0,
            "max_query_attempts": 2,
        }
    )

    assert result["query"] == refined_query

    assert len(
        result["retrieved_chunks"]
    ) == 1

    assert result["query_attempts"] == 2

    assert len(
        retrieval_service.calls
    ) == 2

    assert (
        retrieval_service.calls[0]["query"]
        == original_query
    )

    assert (
        retrieval_service.calls[1]["query"]
        == refined_query
    )


def test_rag_graph_does_not_retry_after_max_attempts():
    """Verify retrieval retry count is bounded."""

    query = "unknown topic"

    retrieval_service = FakeRetrievalService(
        {
            query: [],
        }
    )

    prompt_builder = FakePromptBuilder()
    llm_service = FakeLLMService()

    graph = build_rag_graph(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    result = graph.invoke(
        {
            "user_id": uuid4(),
            "query": query,
            "original_query": query,
            "retrieval_limit": 5,
            "query_attempts": 0,
            "max_query_attempts": 2,
        }
    )

    assert result["retrieved_chunks"] == []

    assert result["query_attempts"] == 2

    assert len(
        retrieval_service.calls
    ) == 2

    assert result["answer"] == (
        "I could not find relevant information "
        "in the available knowledge base to answer "
        "your question."
    )

    assert llm_service.called_with is None

    assert prompt_builder.called_with is None


def test_rag_graph_respects_custom_max_attempts():
    """Verify the graph respects a lower retry limit."""

    query = "unknown topic"

    retrieval_service = FakeRetrievalService(
        {
            query: [],
        }
    )

    prompt_builder = FakePromptBuilder()
    llm_service = FakeLLMService()

    graph = build_rag_graph(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    result = graph.invoke(
        {
            "user_id": uuid4(),
            "query": query,
            "original_query": query,
            "retrieval_limit": 5,
            "query_attempts": 0,
            "max_query_attempts": 1,
        }
    )

    assert result["query_attempts"] == 1

    assert len(
        retrieval_service.calls
    ) == 1

    assert result["answer"] == (
        "I could not find relevant information "
        "in the available knowledge base to answer "
        "your question."
    )

    assert llm_service.called_with is None
