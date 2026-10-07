from uuid import uuid4

from app.services.vector_store import ChromaVectorStore


def create_store(tmp_path):
    """Create an isolated ChromaDB store for tests."""

    return ChromaVectorStore(
        path=str(tmp_path / "chroma"),
        collection_name=f"test_{uuid4().hex}",
    )


def test_vector_store_can_be_created(tmp_path):
    """Verify that the ChromaDB store initializes."""

    store = create_store(tmp_path)

    assert store.client is not None
    assert store.collection is not None


def test_vector_store_can_add_chunk(tmp_path):
    """Verify that a chunk is stored and embedded."""

    store = create_store(tmp_path)

    chunk_id = str(uuid4())

    store.add(
        chunk_id=chunk_id,
        document_id=str(uuid4()),
        document_version_id=str(uuid4()),
        chunk_index=0,
        text="Employee leave policy.",
    )

    result = store.collection.get(
        ids=[chunk_id],
        include=["documents", "embeddings"],
    )

    assert result["ids"] == [chunk_id]
    assert result["documents"] == [
        "Employee leave policy."
    ]

    assert result["embeddings"] is not None
    assert len(result["embeddings"][0]) > 0


def test_vector_store_can_search(tmp_path):
    """Verify semantic search using document text."""

    store = create_store(tmp_path)

    document_id = str(uuid4())
    version_id = str(uuid4())

    store.add(
        chunk_id=str(uuid4()),
        document_id=document_id,
        document_version_id=version_id,
        chunk_index=0,
        text="Employees receive annual leave and holiday benefits.",
    )

    store.add(
        chunk_id=str(uuid4()),
        document_id=document_id,
        document_version_id=version_id,
        chunk_index=1,
        text="The office cafeteria serves lunch from twelve to two.",
    )

    result = store.search(
        query="employee annual leave",
        limit=1,
    )

    assert len(result["ids"][0]) == 1
    assert result["documents"][0][0] == (
        "Employees receive annual leave and holiday benefits."
    )


def test_vector_store_can_delete_chunk(tmp_path):
    """Verify that a chunk can be deleted."""

    store = create_store(tmp_path)

    chunk_id = str(uuid4())

    store.add(
        chunk_id=chunk_id,
        document_id=str(uuid4()),
        document_version_id=str(uuid4()),
        chunk_index=0,
        text="Test document.",
    )

    store.delete(chunk_id)

    result = store.collection.get(
        ids=[chunk_id]
    )

    assert result["ids"] == []
