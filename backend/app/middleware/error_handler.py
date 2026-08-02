from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.core.exceptions import DomainException, NotFoundException, ValidationException, AuthenticationException, AIException
from backend.app.core.logging import error_logger


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
        content={
            "success": False,
            "data": None,
            "message": exc.message,
            "error": {"code": exc.code, "details": exc.message}
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    error_logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": "An unexpected server error occurred.",
            "error": {"code": "INTERNAL_SERVER_ERROR", "details": str(exc)}
        }
    )
