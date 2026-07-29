import time
from starlette.types import ASGIApp, Receive, Scope, Send
from app.core.logging import request_logger


class RequestLoggingMiddleware:
    """
    Pure ASGI middleware for request/response logging.

    Deliberately NOT using BaseHTTPMiddleware because it has a well-known
    Starlette bug: wrapping the response stream causes CORS headers added by
    the outer CORSMiddleware to be stripped from error responses (4xx / 5xx).
    A pure ASGI middleware does not have this problem.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Pass through websocket / lifespan events unchanged
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope.get("method", "")
        path = scope.get("path", "")
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        status_code_holder = [0]

        async def send_with_logging(message):
            if message["type"] == "http.response.start":
                status_code_holder[0] = message.get("status", 0)
            await send(message)

        await self.app(scope, receive, send_with_logging)

        process_time_ms = (time.time() - start_time) * 1000
        request_logger.info(
            f"{method} {path} "
            f"Status:{status_code_holder[0]} "
            f"Duration:{process_time_ms:.2f}ms IP:{client_ip}"
        )
