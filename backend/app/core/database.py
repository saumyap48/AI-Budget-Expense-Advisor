import os
from urllib.parse import urlparse
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


def mask_db_url(raw_url: str) -> str:
    """Safely mask database URL credentials for safe logging without exposing secrets."""
    if not raw_url:
        return "<NOT SET>"
    try:
        parsed = urlparse(raw_url)
        scheme = parsed.scheme or "postgresql"
        host = parsed.hostname or "unknown"
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or ""
        return f"{scheme}://***:***@{host}{port}{path}"
    except Exception:
        return "<CONFIGURED (MASKED)>"


def normalize_db_url(url: str) -> str:
    """Normalize legacy postgres:// or bare postgresql:// scheme to postgresql+psycopg2:// for SQLAlchemy 2."""
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


# Choose database URL: use TEST_DATABASE_URL when running tests
if os.getenv("PYTEST_CURRENT_TEST"):
    db_url = settings.TEST_DATABASE_URL
else:
    db_url = settings.DATABASE_URL

db_url = normalize_db_url(db_url)

# Configure engine options based on dialect
engine_kwargs = {"echo": False}

if db_url.startswith("sqlite"):
    database_path = db_url.replace("sqlite:///", "")
    data_dir = os.path.dirname(database_path)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL connection options (Render compatibility)
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(db_url, **engine_kwargs)

if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a database session and ensures clean closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
