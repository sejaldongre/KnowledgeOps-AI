from fastapi import APIRouter, Depends

from app.schemas.common import APIResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=APIResponse[dict[str, str]],
)
def health_check() -> APIResponse[dict[str, str]]:
    """Return basic application health status."""

    return APIResponse(
        data={
            "status": "healthy",
            "service": "KnowledgeOps AI",
        }
    )


@router.get(
    "/database",
    response_model=APIResponse[dict[str, str]],
)
def database_health_check(
    db: Session = Depends(get_db),
) -> APIResponse[dict[str, str]]:
    """Verify that the application can communicate with PostgreSQL."""

    db.execute(text("SELECT 1"))

    return APIResponse(
        data={
            "status": "healthy",
            "database": "connected",
        }
    )
