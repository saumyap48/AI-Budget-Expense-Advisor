from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BudgetBase(BaseModel):
    monthly_budget: float = Field(..., gt=0, description="Monthly spending limit")
    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    year: int = Field(..., ge=2000, description="Year (e.g. 2026)")


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    monthly_budget: float = Field(..., gt=0)


class BudgetRead(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetStatus(BaseModel):
    id: Optional[int] = None
    monthly_budget: float = 0.0
    month: int
    year: int
    total_spent: float = 0.0
    remaining_balance: float = 0.0
    percentage_spent: float = 0.0
    is_warning: bool = False  # > 80%
    is_exceeded: bool = False  # > 100%
    status_level: str = "normal"  # normal, warning, exceeded
    message: str = "Budget status nominal"
