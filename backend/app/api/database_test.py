from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db


router = APIRouter(
    prefix="/database",
    tags=["Database"],
)


@router.get("/health")
def database_health(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Check whether the API can communicate with PostgreSQL."""
    db.execute(text("SELECT 1"))

    return {"status": "database connection healthy"}
