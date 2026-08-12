import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Choose database URL: use TEST_DATABASE_URL when running tests (pytest sets PYTEST_CURRENT_TEST)
if os.getenv("PYTEST_CURRENT_TEST"):
    db_url = settings.TEST_DATABASE_URL
else:
    db_url = settings.DATABASE_URL

# Create PostgreSQL engine
engine = create_engine(db_url, echo=False)

# Session factory and Base declarative class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a database session and ensures clean closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
