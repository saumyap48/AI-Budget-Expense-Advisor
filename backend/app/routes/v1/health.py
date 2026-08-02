from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
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

    gemini_status = "healthy" if gemini_service.is_available() else "unavailable (check GEMINI_API_KEY)"

    return ApiResponse(
        success=True,
        data={
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "gemini_llm": gemini_status,
            "version": "1.0.0"
        },
        message="System status diagnostic complete"
    )
