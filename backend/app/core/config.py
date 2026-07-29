import sys
import os

# Ensure project root and backend root are in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from typing import List
from pydantic_settings import BaseSettings

# Resolve .env path relative to this config file (always finds backend/.env)
_ENV_FILE = os.path.join(BACKEND_DIR, ".env")


class Settings(BaseSettings):
    APP_NAME: str = "AI Budget & Expense Advisor"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # JWT Security Configuration
    SECRET_KEY: str = "ai_budget_advisor_super_secret_jwt_key_2026_production_ready"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data/finance.db"

    # Vector DB Configuration
    CHROMA_DB_DIR: str = "./vector_store/chroma_db"
    CHROMA_COLLECTION_NAME: str = "expense_vectors"

    # Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # CORS Configuration
    # FRONTEND_URL: set this on Render to the current Vercel deployment URL.
    # Changing it only requires a Render env var update — no code redeploy.
    # The regex in main.py also covers all *.vercel.app URLs as a dynamic fallback.
    FRONTEND_URL: str = "https://ai-budget-expense-advisor-nskycwcu4-saumyap48s-projects.vercel.app"

    ALLOWED_ORIGINS: str = (
        "https://ai-budget-expense-advisor.vercel.app,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:8000,http://127.0.0.1:8000"
    )

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = _ENV_FILE
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
