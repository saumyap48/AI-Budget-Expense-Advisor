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

    # CORS Middleware
    allowed_origins = [
        "https://ai-budget-expense-advisor-aa1tu0jjg-saumyap48s-projects.vercel.app",
        "https://ai-budget-expense-advisor-hjt2lskrr-saumyap48s-projects.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]
    for origin in settings.origins_list:
        if origin and origin not in allowed_origins:
            allowed_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
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
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
