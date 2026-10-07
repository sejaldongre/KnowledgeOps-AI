from uuid import uuid4

from app.services.rag import RAGPromptBuilder
from app.services.retrieval import RetrievalResult


def test_prompt_contains_user_question():
    """Verify the user's question is included."""

    builder = RAGPromptBuilder()

    prompt = builder.build(
        query="What is the leave policy?",
        results=[],
    )

    assert "What is the leave policy?" in prompt


def test_prompt_contains_retrieved_context():
    """Verify retrieved document text is included."""

    document_id = uuid4()
    version_id = uuid4()

    result = RetrievalResult(
        chunk_id=str(uuid4()),
        document_id=document_id,
        document_version_id=version_id,
        chunk_index=0,
        text="Employees receive twenty paid leave days.",
        distance=0.12,
    )

    builder = RAGPromptBuilder()

    prompt = builder.build(
        query="How many leave days do employees receive?",
        results=[result],
    )

    assert (
        "Employees receive twenty paid leave days."
        in prompt
    )

    assert str(document_id) in prompt
    assert str(version_id) in prompt
    assert "Chunk Index: 0" in prompt


def test_prompt_contains_multiple_sources():
    """Verify multiple retrieved chunks are included."""

    first = RetrievalResult(
        chunk_id=str(uuid4()),
        document_id=uuid4(),
        document_version_id=uuid4(),
        chunk_index=0,
        text="Employees receive annual leave.",
        distance=0.10,
    )

    second = RetrievalResult(
        chunk_id=str(uuid4()),
        document_id=uuid4(),
        document_version_id=uuid4(),
        chunk_index=1,
        text="Leave requests require manager approval.",
        distance=0.20,
    )

    builder = RAGPromptBuilder()

    prompt = builder.build(
        query="What are the leave rules?",
        results=[first, second],
    )

    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt

    assert (
        "Employees receive annual leave."
        in prompt
    )

    assert (
        "Leave requests require manager approval."
        in prompt
    )


def test_prompt_handles_no_results():
    """Verify missing context is explicitly represented."""

    builder = RAGPromptBuilder()

    prompt = builder.build(
        query="What is the cafeteria policy?",
        results=[],
    )

    assert (
        "No relevant information was found"
        in prompt
    )

    assert "What is the cafeteria policy?" in prompt


def test_prompt_contains_grounding_instructions():
    """Verify hallucination-prevention instructions exist."""

    builder = RAGPromptBuilder()

    prompt = builder.build(
        query="What is the leave policy?",
        results=[],
    )

    assert (
        "Do not invent facts"
        in prompt
    )

    assert (
        "provided knowledge context"
        in prompt
    )