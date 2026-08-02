from typing import List, Optional
from datetime import date as DateType
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseRead, ExpenseFilter
from app.services.expense_service import ExpenseService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=ApiResponse[List[ExpenseRead]])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[DateType] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[DateType] = Query(None, description="End date YYYY-MM-DD"),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    q: Optional[str] = Query(None, description="Search description or notes"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("date", pattern="^(date|amount|category|created_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ExpenseService(db)
    filters = ExpenseFilter(
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        q=q
    )
    items, total_records = service.list_expenses(
        user_id=current_user.id, filters=filters, page=page, limit=limit, sort_by=sort_by, order=order
    )

    total_pages = (total_records + limit - 1) // limit if total_records > 0 else 1
    meta = PaginationMeta(
        page=page,
        limit=limit,
        total_records=total_records,
        total_pages=total_pages
    )

    data = [ExpenseRead.from_orm(item) for item in items]
    return ApiResponse(success=True, data=data, message="Expenses retrieved successfully", meta=meta)


@router.post("", response_model=ApiResponse[ExpenseRead], status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ExpenseService(db)
    created = service.create_expense(payload, user_id=current_user.id)
    return ApiResponse(
        success=True,
        data=ExpenseRead.from_orm(created),
        message="Expense recorded successfully and synced with vector store"
    )


@router.get("/{expense_id}", response_model=ApiResponse[ExpenseRead])
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ExpenseService(db)
    item = service.get_expense(expense_id, user_id=current_user.id)
    return ApiResponse(success=True, data=ExpenseRead.from_orm(item), message="Expense retrieved successfully")


@router.put("/{expense_id}", response_model=ApiResponse[ExpenseRead])
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ExpenseService(db)
    updated = service.update_expense(expense_id, user_id=current_user.id, data=payload)
    return ApiResponse(
        success=True,
        data=ExpenseRead.from_orm(updated),
        message="Expense updated successfully and vector index synced"
    )


@router.delete("/{expense_id}", response_model=ApiResponse[dict])
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ExpenseService(db)
    service.delete_expense(expense_id, user_id=current_user.id)
    return ApiResponse(success=True, data={"id": expense_id}, message="Expense deleted successfully")
