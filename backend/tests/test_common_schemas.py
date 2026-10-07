from app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationMeta,
)


def test_api_response():
    """Verify the standard API response."""

    response = APIResponse[str](
        data="KnowledgeOps AI",
    )

    assert response.success is True
    assert response.data == "KnowledgeOps AI"


def test_paginated_response():
    """Verify the paginated API response."""

    response = PaginatedResponse[list[str]](
        data=["Document 1", "Document 2"],
        pagination=PaginationMeta(
            page=1,
            page_size=10,
            total=2,
            total_pages=1,
        ),
    )

    assert response.success is True
    assert len(response.data) == 2
    assert response.pagination.total == 2
