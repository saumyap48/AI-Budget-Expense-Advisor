import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import logger
from app.core.exceptions import DomainException
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.error_handler import domain_exception_handler, global_exception_handler
from app.routes.api_v1 import api_v1_router


# ---------------------------------------------------------------------------
# Lifespan: runs AFTER uvicorn binds the port — safe for Render port scan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle managed by uvicorn after socket bind."""
    # ── Startup ──────────────────────────────────────────────────────────────
    # Database table creation — deferred so the port is already bound.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified / created.")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"DB create_all failed (non-fatal): {exc}")

    # ChromaDB / fallback vector-store singleton — deferred for same reason.
    try:
        from app.services.chroma_service import chroma_service  # noqa: F401
        logger.info("ChromaDB / vector-store initialised.")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Vector-store init failed (non-fatal): {exc}")

    logger.info(
        f"Application startup complete — HOST=0.0.0.0 PORT={os.environ.get('PORT', settings.PORT)}"
    )
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("Application shutdown.")

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Personal Finance & Expense Advisor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# Starlette processes middlewares in REVERSE registration order.
# The LAST middleware added runs FIRST on every incoming request.
# CORSMiddleware MUST be added last so it is the outermost layer.
#
# Registration order (outermost → innermost at runtime):
#   CORSMiddleware  ← outermost, handles OPTIONS preflights & injects headers
#   RequestLoggingMiddleware
#   Application routes
# ---------------------------------------------------------------------------

# 1. Logging middleware — added first, so it runs SECOND at runtime.
#    Implemented as a pure ASGI callable (NOT BaseHTTPMiddleware) to avoid
#    the known Starlette bug where BaseHTTPMiddleware strips CORS headers
#    from error responses before CORSMiddleware can attach them.
app.add_middleware(RequestLoggingMiddleware)

# 2. CORS middleware — added LAST, so it runs FIRST at runtime.
#    Explicitly list every known origin AND use allow_origin_regex as a
#    dynamic catch-all for all Vercel preview/production deployments.
#    With allow_credentials=True, Starlette reflects the exact requesting
#    origin back (never a bare "*"), which satisfies browser CORS rules.
CORS_ORIGINS = [
    # Production Vercel deployment (stable alias)
    "https://ai-budget-expense-advisor.vercel.app",
    # Current Vercel preview / deployment URL (set FRONTEND_URL on Render)
    settings.FRONTEND_URL,
    # Local development
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
# Deduplicate while preserving order (in case FRONTEND_URL matches a listed origin)
seen = set()
CORS_ORIGINS_DEDUPED = [x for x in CORS_ORIGINS if not (x in seen or seen.add(x))]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_DEDUPED,
    allow_origin_regex=r"https://.*\.vercel\.app",   # covers ALL *.vercel.app URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# These are NOT middleware — they do not affect the middleware stack order.
# ---------------------------------------------------------------------------
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ---------------------------------------------------------------------------
# Routers — always included AFTER middleware is configured
# ---------------------------------------------------------------------------
app.include_router(api_v1_router)


# ---------------------------------------------------------------------------
# Root & health endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "api_version": "/api/v1",
    }


# ---------------------------------------------------------------------------
# Optional: serve bundled frontend static files
# ---------------------------------------------------------------------------
_frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)
if os.path.exists(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

    @app.get("/app", include_in_schema=False)
    def serve_frontend_index():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))


logger.info(
    "FastAPI application initialised. "
    f"CORS origins: {CORS_ORIGINS_DEDUPED} + regex *.vercel.app"
)

# ---------------------------------------------------------------------------
# Local dev entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
