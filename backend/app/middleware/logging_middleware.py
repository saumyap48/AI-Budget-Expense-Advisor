import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.logging import request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time_ms = (time.time() - start_time) * 1000
        status_code = response.status_code
        client_ip = request.client.host if request.client else "unknown"

        request_logger.info(
            f"{request.method} {request.url.path} "
            f"Status:{status_code} Duration:{process_time_ms:.2f}ms IP:{client_ip}"
        )

        return response
