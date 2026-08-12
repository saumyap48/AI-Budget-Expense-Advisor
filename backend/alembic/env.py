import os
from dotenv import load_dotenv

# Load .env if present (local dev). On Render the env var is already in the environment.
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

# ---------------------------------------------------------------------------
# Alembic config object
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Database URL — normalise Render's legacy postgres:// scheme to the
# postgresql+psycopg2:// dialect that SQLAlchemy 2 requires.
# ---------------------------------------------------------------------------
_raw_url = os.getenv("DATABASE_URL")

if not _raw_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Set it in the Render dashboard (or your local .env file)."
    )

if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif _raw_url.startswith("postgresql://") and "+psycopg2" not in _raw_url:
    _raw_url = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

DATABASE_URL = _raw_url

# Escape % characters for ConfigParser interpolation
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))

# ---------------------------------------------------------------------------
# Import all ORM models so Alembic can autogenerate accurate migrations
# ---------------------------------------------------------------------------
from app.models import Base  # noqa: E402  (models registers User, Expense, Budget)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the database)."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
