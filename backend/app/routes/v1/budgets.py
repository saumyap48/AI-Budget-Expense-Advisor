from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.budget import BudgetCreate, BudgetStatus
from backend.app.services.budget_service import BudgetService
from backend.app.dependencies.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=ApiResponse[BudgetStatus])
@router.get("/current", response_model=ApiResponse[BudgetStatus])
def get_current_budget(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BudgetService(db)
    budget_status = service.get_current_budget_status(user_id=current_user.id, month=month, year=year)
    return ApiResponse(
        success=True,
        data=budget_status,
        message=budget_status.message
    )


@router.post("", response_model=ApiResponse[BudgetStatus], status_code=status.HTTP_201_CREATED)
@router.put("", response_model=ApiResponse[BudgetStatus])
def set_or_update_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BudgetService(db)
    status_result = service.set_budget(user_id=current_user.id, data=payload)
    return ApiResponse(
        success=True,
        data=status_result,
        message="Monthly budget updated successfully"
    )
