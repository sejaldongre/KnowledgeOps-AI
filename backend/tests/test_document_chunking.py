import pytest

from app.services.document_chunking import (
    DocumentChunkingService,
)


def test_chunk_empty_text():
    """Verify that empty text produces no chunks."""

    service = DocumentChunkingService()

    result = service.chunk("")

    assert result == []


def test_chunk_small_text():
    """Verify that short text produces one chunk."""

    service = DocumentChunkingService(
        chunk_size=100,
        chunk_overlap=20,
    )

    result = service.chunk(
        "Employee Handbook"
    )

    assert len(result) == 1
    assert result[0].text == "Employee Handbook"
    assert result[0].chunk_index == 0


def test_chunk_large_text():
    """Verify that long text is split into multiple chunks."""

    service = DocumentChunkingService(
        chunk_size=100,
        chunk_overlap=20,
    )

    text = "A" * 250

    result = service.chunk(text)

    assert len(result) == 4

    assert len(result[0].text) == 100
    assert len(result[1].text) == 100
    assert len(result[2].text) == 90
    assert len(result[3].text) == 10


def test_chunk_overlap_is_preserved():
    """Verify that consecutive chunks share overlapping text."""

    service = DocumentChunkingService(
        chunk_size=10,
        chunk_overlap=3,
    )

    text = "ABCDEFGHIJKLMNO"

    result = service.chunk(text)

    assert result[0].text == "ABCDEFGHIJ"
    assert result[1].text.startswith("HIJKLM")


def test_chunk_indexes_are_sequential():
    """Verify that chunk indexes start at zero."""

    service = DocumentChunkingService(
        chunk_size=10,
        chunk_overlap=2,
    )

    text = "A" * 35

    result = service.chunk(text)

    indexes = [
        chunk.chunk_index
        for chunk in result
    ]

    assert indexes == list(range(len(result)))


def test_chunk_size_must_be_positive():
    """Verify invalid chunk size is rejected."""

    with pytest.raises(ValueError):
        DocumentChunkingService(
            chunk_size=0,
            chunk_overlap=0,
        )


def test_chunk_overlap_cannot_be_negative():
    """Verify negative overlap is rejected."""

    with pytest.raises(ValueError):
        DocumentChunkingService(
            chunk_size=100,
            chunk_overlap=-1,
        )


def test_chunk_overlap_must_be_smaller_than_size():
    """Verify overlap cannot equal or exceed chunk size."""

    with pytest.raises(ValueError):
        DocumentChunkingService(
            chunk_size=100,
            chunk_overlap=100,
        )

    with pytest.raises(ValueError):
        DocumentChunkingService(
            chunk_size=100,
            chunk_overlap=150,
        )
