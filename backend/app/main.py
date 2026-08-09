import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Knowledge Management and RAG Platform",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic API information."""
    logger.info("Root endpoint requested")

    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }
