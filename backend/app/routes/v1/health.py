import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db, mask_db_url
from app.core.config import settings
from app.schemas.common import ApiResponse
from app.services.gemini_service import gemini_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[dict])
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    raw_env_url = os.getenv("DATABASE_URL", "")
    db_env_configured = bool(raw_env_url and "localhost" not in raw_env_url and "127.0.0.1" not in raw_env_url)
    gemini_status = "healthy" if gemini_service.is_available() else "unavailable (check GEMINI_API_KEY)"

    return ApiResponse(
        success=True,
        data={
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "database_env_configured": db_env_configured,
            "database_target": mask_db_url(settings.DATABASE_URL),
            "gemini_llm": gemini_status,
            "version": "1.0.0"
        },
        message="System status diagnostic complete"
    )
