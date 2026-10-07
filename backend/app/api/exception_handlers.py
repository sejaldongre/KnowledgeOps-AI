from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Convert application exceptions into consistent API responses."""

    status_code = 400

    if exc.code == "RESOURCE_NOT_FOUND":
        status_code = 404
    elif exc.code == "UNAUTHORIZED":
        status_code = 401
    elif exc.code == "FORBIDDEN":
        status_code = 403
    elif exc.code == "PERMISSION_ALREADY_EXISTS":
        status_code = 409

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
