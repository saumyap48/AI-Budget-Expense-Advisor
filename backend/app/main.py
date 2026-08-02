import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.logging import logger
from backend.app.core.exceptions import DomainException
from backend.app.middleware.logging_middleware import RequestLoggingMiddleware
from backend.app.middleware.error_handler import domain_exception_handler, global_exception_handler
from backend.app.routes.api_v1 import api_v1_router


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

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Audit Logging Middleware
    app.add_middleware(RequestLoggingMiddleware)

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
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
