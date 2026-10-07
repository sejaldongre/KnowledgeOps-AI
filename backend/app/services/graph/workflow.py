from langgraph.graph import END, START, StateGraph

from app.services.graph.nodes import RAGGraphNodes
from app.services.graph.state import RAGGraphState
from app.services.llm.base import LLMService
from app.services.rag import RAGPromptBuilder
from app.services.retrieval import RetrievalService


def _should_refine(
    state: RAGGraphState,
) -> str:
    """Decide whether retrieval should be retried."""

    retrieved_chunks = state.get(
        "retrieved_chunks",
        [],
    )

    attempts = state.get(
        "query_attempts",
        0,
    )

    max_attempts = state.get(
        "max_query_attempts",
        2,
    )

    if retrieved_chunks:
        return "build_prompt"

    if attempts < max_attempts:
        return "refine_query"

    return "no_context"


def build_rag_graph(
    *,
    retrieval_service: RetrievalService,
    prompt_builder: RAGPromptBuilder,
    llm_service: LLMService,
):
    """Build the conditional RAG workflow."""

    nodes = RAGGraphNodes(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    graph = StateGraph(RAGGraphState)

    graph.add_node(
        "retrieve",
        nodes.retrieve,
    )

    graph.add_node(
        "refine_query",
        nodes.refine_query,
    )

    graph.add_node(
        "build_prompt",
        nodes.build_prompt,
    )

    graph.add_node(
        "generate",
        nodes.generate,
    )

    graph.add_node(
        "no_context",
        nodes.no_context,
    )

    graph.add_edge(
        START,
        "retrieve",
    )

    graph.add_conditional_edges(
        "retrieve",
        _should_refine,
        {
            "refine_query": "refine_query",
            "build_prompt": "build_prompt",
            "no_context": "no_context",
        },
    )

    graph.add_edge(
        "refine_query",
        "retrieve",
    )

    graph.add_edge(
        "build_prompt",
        "generate",
    )

    graph.add_edge(
        "generate",
        END,
    )

    graph.add_edge(
        "no_context",
        END,
    )

    return graph.compile()
