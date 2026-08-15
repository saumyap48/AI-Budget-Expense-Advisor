import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file in the project root (backend)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "AI Budget & Expense Advisor")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # JWT Security Configuration
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "ai_budget_advisor_super_secret_jwt_key_2026_production_ready",
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Database Configuration
    @property
    def DATABASE_URL(self) -> str:
        """
        Get DATABASE_URL from environment.
        In production (or Render), DATABASE_URL is strictly required. If missing, fail immediately
        with a descriptive RuntimeError instead of silently connecting to localhost.
        In local development, default to local PostgreSQL connection.
        """
        url = os.getenv("DATABASE_URL")
        if not url:
            is_production = (
                os.getenv("APP_ENV") == "production"
                or "RENDER" in os.environ
                or "RENDER_SERVICE_ID" in os.environ
            )
            if is_production:
                raise RuntimeError(
                    "DATABASE_URL environment variable is missing in production environment. "
                    "Set DATABASE_URL in your Render Web Service Environment Settings using your Render PostgreSQL Internal Connection String."
                )
            return "postgresql+psycopg2://expense_user:your_password@localhost:5432/expense_tracker"
        return url

    TEST_DATABASE_URL: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://expense_user:your_password@localhost:5432/expense_tracker_test",
    )

    # Vector DB Configuration
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./vector_store/chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "expense_vectors")

    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # CORS Configuration
    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "https://ai-budget-expense-advisor-nskycwcu4-saumyap48s-projects.vercel.app",
    )

    # CORS Configuration (comma-separated list)
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "https://ai-budget-expense-advisor.vercel.app,http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000",
    )

    @property
    def origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a clean list of URLs."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Export a singleton instance used throughout the project
settings = Settings()
