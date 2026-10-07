from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for semantic document search."""

    query: str = Field(
        min_length=1,
        description="Natural-language search query.",
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results.",
    )


class SearchResult(BaseModel):
    """A single semantic search result."""

    chunk_id: str
    document_id: UUID
    document_version_id: UUID
    chunk_index: int
    text: str
    distance: float | None = None


class SearchResponse(BaseModel):
    """Response containing semantic search results."""

    query: str
    results: list[SearchResult]
