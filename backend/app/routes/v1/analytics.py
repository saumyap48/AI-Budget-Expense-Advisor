from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.analytics import AnalyticsSummary
from backend.app.services.analytics_service import AnalyticsService
from backend.app.dependencies.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=ApiResponse[AnalyticsSummary])
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AnalyticsService(db)
    summary = service.get_analytics_summary(user_id=current_user.id)
    return ApiResponse(
        success=True,
        data=summary,
        message="Analytics summary generated successfully"
    )
