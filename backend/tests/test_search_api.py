from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user,
    get_retrieval_service,
)
from app.main import app
from app.services.retrieval import RetrievalResult


USER_ID = uuid4()


class FakeUser:
    """Fake authenticated user for search API tests."""

    def __init__(self):
        self.id = USER_ID
        self.email = "search@example.com"
        self.full_name = "Search User"
        self.is_active = True


class FakeRetrievalService:
    """Fake retrieval service for search API tests."""

    def __init__(self, results=None):
        self.results = results or []
        self.called_with = None

    def search(
        self,
        *,
        query,
        user_id,
        limit,
    ):
        self.called_with = {
            "query": query,
            "user_id": user_id,
            "limit": limit,
        }

        return self.results


@pytest.fixture
def fake_user():
    """Return a fake authenticated user."""

    return FakeUser()


@pytest.fixture
def retrieval_service():
    """Return a fake retrieval service."""

    return FakeRetrievalService()


@pytest.fixture
def client(fake_user, retrieval_service):
    """Create a test client with overridden dependencies."""

    def override_current_user():
        return fake_user

    def override_retrieval_service():
        return retrieval_service

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    app.dependency_overrides[
        get_retrieval_service
    ] = override_retrieval_service

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_search_returns_results(
    client,
    fake_user,
    retrieval_service,
):
    """Verify the search API returns retrieved chunks."""

    document_id = uuid4()
    version_id = uuid4()
    chunk_id = str(uuid4())

    retrieval_service.results = [
        RetrievalResult(
            chunk_id=chunk_id,
            document_id=document_id,
            document_version_id=version_id,
            chunk_index=0,
            text="Employees receive twenty paid leave days.",
            distance=0.15,
        )
    ]

    response = client.post(
        "/search",
        json={
            "query": "employee leave policy",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "employee leave policy"
    assert len(body["results"]) == 1

    result = body["results"][0]

    assert result["chunk_id"] == chunk_id
    assert result["document_id"] == str(document_id)
    assert result["document_version_id"] == str(
        version_id
    )
    assert result["chunk_index"] == 0
    assert (
        result["text"]
        == "Employees receive twenty paid leave days."
    )
    assert result["distance"] == 0.15

    assert retrieval_service.called_with == {
        "query": "employee leave policy",
        "user_id": fake_user.id,
        "limit": 5,
    }


def test_search_passes_custom_limit(
    client,
    fake_user,
    retrieval_service,
):
    """Verify a custom result limit reaches the service."""

    response = client.post(
        "/search",
        json={
            "query": "leave policy",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    assert retrieval_service.called_with == {
        "query": "leave policy",
        "user_id": fake_user.id,
        "limit": 10,
    }


def test_search_returns_empty_results(
    client,
    retrieval_service,
):
    """Verify a search with no matches returns an empty list."""

    retrieval_service.results = []

    response = client.post(
        "/search",
        json={
            "query": "unknown information",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "unknown information"
    assert body["results"] == []


def test_search_rejects_blank_query(
    client,
):
    """Verify blank queries fail request validation."""

    response = client.post(
        "/search",
        json={
            "query": "",
            "limit": 5,
        },
    )

    assert response.status_code == 422


def test_search_rejects_limit_above_maximum(
    client,
):
    """Verify limits above 20 are rejected."""

    response = client.post(
        "/search",
        json={
            "query": "leave policy",
            "limit": 21,
        },
    )

    assert response.status_code == 422


def test_search_rejects_limit_below_minimum(
    client,
):
    """Verify limits below 1 are rejected."""

    response = client.post(
        "/search",
        json={
            "query": "leave policy",
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_search_requires_authentication():
    """Verify unauthenticated requests are rejected."""

    client = TestClient(app)

    response = client.post(
        "/search",
        json={
            "query": "leave policy",
            "limit": 5,
        },
    )

    assert response.status_code in {401, 403}
