from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import (
    DomainException,
    NotFoundException,
    ValidationException,
    AuthenticationException,
    AIException,
)
from app.core.logging import error_logger


def _cors_headers(request: Request) -> dict:
    """
    Return CORS headers that mirror the requesting origin back to the client.

    FastAPI exception handlers run INSIDE the middleware stack, so their
    JSONResponse objects pass back through CORSMiddleware on the way out —
    CORSMiddleware will attach the correct Access-Control-Allow-Origin header
    automatically as long as the response goes through the normal send path.

    However, to be defensive (e.g. if a future refactor changes the stack),
    we also inject the header here so error responses are always CORS-safe.
    """
    origin = request.headers.get("origin", "")
    return {"Access-Control-Allow-Origin": origin} if origin else {}


async def domain_exception_handler(request: Request, exc: DomainException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AIException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        headers=_cors_headers(request),
        content={
            "success": False,
            "data": None,
            "message": exc.message,
            "error": {"code": exc.code, "details": exc.message},
        },
    )


async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    error_logger.error(
        f"Database error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers=_cors_headers(request),
        content={
            "success": False,
            "data": None,
            "message": "Database connection error. Please verify database environment configuration.",
            "error": {"code": "DATABASE_ERROR", "details": str(exc)},
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    error_logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers=_cors_headers(request),
        content={
            "success": False,
            "data": None,
            "message": "An unexpected server error occurred.",
            "error": {"code": "INTERNAL_SERVER_ERROR", "details": str(exc)},
        },
    )
