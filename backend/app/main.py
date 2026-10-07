import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.conversation import router as conversation_router
from app.api.database_test import router as database_router
from app.api.document import router as document_router
from app.api.exception_handlers import app_exception_handler
from app.api.health import router as health_router
from app.api.permissions import router as permissions_router
from app.api.rbac import router as rbac_router
from app.api.search import router as search_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging


configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Knowledge Management and RAG Platform",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://knowledge-ops-ai-three.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(
    AppException,
    app_exception_handler,
)


app.include_router(health_router)
app.include_router(database_router)
app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(permissions_router)
app.include_router(document_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(conversation_router)


@app.get("/")
async def root() -> dict[str, str]:
    logger.info("Root endpoint requested")

    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }
