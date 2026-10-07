from uuid import uuid4

from app.models.document_permission import PermissionLevel
from app.services.retrieval import RetrievalService


class FakeVectorStore:
    """Fake Chroma vector store for retrieval tests."""

    def __init__(self, results):
        self.results = results
        self.called_with = None

    def search(self, *, query, limit):
        self.called_with = {
            "query": query,
            "limit": limit,
        }

        return self.results


class FakePermissionService:
    """Fake permission service for retrieval tests."""

    def __init__(self, allowed_documents):
        self.allowed_documents = allowed_documents
        self.checked_documents = []

    def has_permission(
        self,
        *,
        user_id,
        document_id,
        permission,
    ):
        self.checked_documents.append(
            {
                "user_id": user_id,
                "document_id": document_id,
                "permission": permission,
            }
        )

        return document_id in self.allowed_documents


def create_result(
    *,
    document_id,
    version_id,
    chunk_id,
    chunk_index,
    text,
    distance,
):
    return {
        "ids": [[chunk_id]],
        "documents": [[text]],
        "metadatas": [
            [
                {
                    "document_id": str(document_id),
                    "document_version_id": str(version_id),
                    "chunk_index": chunk_index,
                }
            ]
        ],
        "distances": [[distance]],
    }


def create_multiple_results(results):
    """Create a Chroma-like response containing multiple chunks."""

    return {
        "ids": [
            [
                result["chunk_id"]
                for result in results
            ]
        ],
        "documents": [
            [
                result["text"]
                for result in results
            ]
        ],
        "metadatas": [
            [
                {
                    "document_id": str(
                        result["document_id"]
                    ),
                    "document_version_id": str(
                        result["version_id"]
                    ),
                    "chunk_index": result["chunk_index"],
                }
                for result in results
            ]
        ],
        "distances": [
            [
                result["distance"]
                for result in results
            ]
        ],
    }


def test_retrieval_returns_authorized_chunk():
    """Verify authorized chunks are returned."""

    user_id = uuid4()
    document_id = uuid4()
    version_id = uuid4()
    chunk_id = str(uuid4())

    vector_store = FakeVectorStore(
        create_result(
            document_id=document_id,
            version_id=version_id,
            chunk_id=chunk_id,
            chunk_index=0,
            text="Annual leave policy.",
            distance=0.12,
        )
    )

    permission_service = FakePermissionService(
        {document_id}
    )

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    result = service.search(
        query="leave policy",
        user_id=user_id,
        limit=5,
    )

    assert len(result) == 1

    retrieved = result[0]

    assert retrieved.chunk_id == chunk_id
    assert retrieved.document_id == document_id
    assert retrieved.document_version_id == version_id
    assert retrieved.chunk_index == 0
    assert retrieved.text == "Annual leave policy."
    assert retrieved.distance == 0.12


def test_retrieval_filters_unauthorized_chunk():
    """Verify unauthorized chunks are not returned."""

    user_id = uuid4()
    document_id = uuid4()
    version_id = uuid4()
    chunk_id = str(uuid4())

    vector_store = FakeVectorStore(
        create_result(
            document_id=document_id,
            version_id=version_id,
            chunk_id=chunk_id,
            chunk_index=0,
            text="Private company information.",
            distance=0.10,
        )
    )

    permission_service = FakePermissionService(
        set()
    )

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    result = service.search(
        query="company information",
        user_id=user_id,
        limit=5,
    )

    assert result == []

    assert (
        permission_service.checked_documents[0][
            "document_id"
        ]
        == document_id
    )

    assert (
        permission_service.checked_documents[0][
            "permission"
        ]
        == PermissionLevel.VIEW
    )


def test_retrieval_returns_empty_for_blank_query():
    """Verify blank queries return no results."""

    vector_store = FakeVectorStore({})
    permission_service = FakePermissionService(set())

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    result = service.search(
        query="   ",
        user_id=uuid4(),
        limit=5,
    )

    assert result == []
    assert vector_store.called_with is None


def test_retrieval_returns_empty_for_invalid_limit():
    """Verify non-positive limits return no results."""

    vector_store = FakeVectorStore({})
    permission_service = FakePermissionService(set())

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    result = service.search(
        query="leave policy",
        user_id=uuid4(),
        limit=0,
    )

    assert result == []
    assert vector_store.called_with is None


def test_retrieval_passes_expanded_limit_to_vector_store():
    """Verify retrieval requests extra candidates for permission filtering."""

    user_id = uuid4()
    document_id = uuid4()
    version_id = uuid4()
    chunk_id = str(uuid4())

    vector_store = FakeVectorStore(
        create_result(
            document_id=document_id,
            version_id=version_id,
            chunk_id=chunk_id,
            chunk_index=0,
            text="Leave policy.",
            distance=0.15,
        )
    )

    permission_service = FakePermissionService(
        {document_id}
    )

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    service.search(
        query="employee leave",
        user_id=user_id,
        limit=3,
    )

    assert vector_store.called_with == {
        "query": "employee leave",
        "limit": 9,
    }


def test_retrieval_stops_after_requested_authorized_results():
    """Verify only the requested number of authorized results is returned."""

    user_id = uuid4()

    authorized_document_1 = uuid4()
    authorized_document_2 = uuid4()
    authorized_document_3 = uuid4()

    version_1 = uuid4()
    version_2 = uuid4()
    version_3 = uuid4()

    results = [
        {
            "document_id": uuid4(),
            "version_id": uuid4(),
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Private result one.",
            "distance": 0.05,
        },
        {
            "document_id": authorized_document_1,
            "version_id": version_1,
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Authorized result one.",
            "distance": 0.10,
        },
        {
            "document_id": uuid4(),
            "version_id": uuid4(),
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Private result two.",
            "distance": 0.15,
        },
        {
            "document_id": authorized_document_2,
            "version_id": version_2,
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Authorized result two.",
            "distance": 0.20,
        },
        {
            "document_id": uuid4(),
            "version_id": uuid4(),
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Private result three.",
            "distance": 0.25,
        },
        {
            "document_id": authorized_document_3,
            "version_id": version_3,
            "chunk_id": str(uuid4()),
            "chunk_index": 0,
            "text": "Authorized result three.",
            "distance": 0.30,
        },
    ]

    vector_store = FakeVectorStore(
        create_multiple_results(results)
    )

    permission_service = FakePermissionService(
        {
            authorized_document_1,
            authorized_document_2,
            authorized_document_3,
        }
    )

    service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    retrieved = service.search(
        query="employee policy",
        user_id=user_id,
        limit=2,
    )

    assert len(retrieved) == 2

    assert retrieved[0].document_id == (
        authorized_document_1
    )

    assert retrieved[1].document_id == (
        authorized_document_2
    )

    assert vector_store.called_with == {
        "query": "employee policy",
        "limit": 6,
    }
