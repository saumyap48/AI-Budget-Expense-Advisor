from datetime import date as DateType, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


VALID_CATEGORIES = [
    "Food", "Shopping", "Transport", "Medical",
    "Entertainment", "Bills", "Education", "Travel", "Others"
]


class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount must be greater than zero")
    category: str = Field(..., description="Category of spending")
    description: str = Field(..., min_length=1, max_length=255, description="Short summary of expense")
    date: DateType = Field(..., description="Date of expense (YYYY-MM-DD)")
    payment_method: Optional[str] = Field("Cash", max_length=30)
    notes: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        formatted = value.strip().title()
        if formatted not in VALID_CATEGORIES:
            # Allow fallback if title match fails, check case-insensitive match
            matches = [c for c in VALID_CATEGORIES if c.lower() == value.strip().lower()]
            if matches:
                return matches[0]
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return formatted


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[DateType] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        formatted = value.strip().title()
        matches = [c for c in VALID_CATEGORIES if c.lower() == value.strip().lower()]
        if matches:
            return matches[0]
        raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")


class ExpenseRead(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseFilter(BaseModel):
    category: Optional[str] = None
    start_date: Optional[DateType] = None
    end_date: Optional[DateType] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    q: Optional[str] = None
