from typing import Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standard successful API response."""

    success: bool = True
    data: DataT


class PaginationMeta(BaseModel):
    """Pagination information."""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard paginated API response."""

    success: bool = True
    data: DataT
    pagination: PaginationMeta
