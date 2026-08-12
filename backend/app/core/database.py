import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Choose database URL: use TEST_DATABASE_URL when running tests
if os.getenv("PYTEST_CURRENT_TEST"):
    db_url = settings.TEST_DATABASE_URL
else:
    db_url = settings.DATABASE_URL

# Fix Render / Heroku legacy postgres:// schema (resolves NoSuchModuleError e3q8)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and "+psycopg2" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

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
