import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import logger
from app.core.exceptions import DomainException
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.error_handler import domain_exception_handler, global_exception_handler
from app.routes.api_v1 import api_v1_router


def create_app() -> FastAPI:
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.APP_NAME,
        description="Local AI-powered Personal Finance & Expense Advisor with RAG and Llama 3",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Request Audit Logging Middleware (registered first → runs second in stack)
    app.add_middleware(RequestLoggingMiddleware)

    # CORS Middleware — must be registered LAST so it runs FIRST on every request.
    # Starlette processes middlewares in reverse-registration order.
    #
    # Explicit origins are guaranteed exact-match by CORSMiddleware.
    # allow_origin_regex is a dynamic catch-all for all *.vercel.app deployments.
    #
    # To update the allowed frontend URL on Render: change the FRONTEND_URL env var.
    # No code redeploy needed — just restart the Render service.
    allowed_origins = [
        # Current Vercel deployment URL (set FRONTEND_URL env var on Render)
        settings.FRONTEND_URL,
        # Stable Vercel production domain
        "https://ai-budget-expense-advisor.vercel.app",
        # Local development servers
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        # Covers ALL *.vercel.app preview/production deployments
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Mount API v1 Routes
    app.include_router(api_v1_router)

    # Root & Health check
    @app.get("/", tags=["Health"])
    def root():
        return {
            "app": settings.APP_NAME,
            "status": "online",
            "docs": "/docs",
            "api_version": "/api/v1"
        }

    # Serve static frontend files if directory exists
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
    if os.path.exists(frontend_dir):
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

        @app.get("/app", include_in_schema=False)
        def serve_frontend_index():
            return FileResponse(os.path.join(frontend_dir, "index.html"))

    logger.info("FastAPI application initialized successfully.")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
