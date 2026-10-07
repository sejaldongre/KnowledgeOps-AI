from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_user,
    get_retrieval_service,
)
from app.models.user import User
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.retrieval import RetrievalService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post(
    "",
    response_model=SearchResponse,
)
def search_documents(
    data: SearchRequest,
    current_user: User = Depends(
        get_current_user
    ),
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
) -> SearchResponse:
    """Search documents accessible to the current user."""

    results = retrieval_service.search(
        query=data.query,
        user_id=current_user.id,
        limit=data.limit,
    )

    return SearchResponse(
        query=data.query,
        results=[
            SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                document_version_id=(
                    result.document_version_id
                ),
                chunk_index=result.chunk_index,
                text=result.text,
                distance=result.distance,
            )
            for result in results
        ],
    )
