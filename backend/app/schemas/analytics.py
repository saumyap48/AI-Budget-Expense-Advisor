from typing import List, Dict, Optional
from pydantic import BaseModel
from backend.app.schemas.expense import ExpenseRead


class CategorySpending(BaseModel):
    category: str
    total_amount: float
    percentage: float
    count: int


class TrendPoint(BaseModel):
    period: str  # Date string or Label (e.g., "2026-07-20", "Week 29", "July 2026")
    amount: float


class AnalyticsSummary(BaseModel):
    total_expenses: float
    total_count: int
    average_daily_spending: float
    highest_spending_category: Optional[CategorySpending] = None
    lowest_spending_category: Optional[CategorySpending] = None
    category_breakdown: List[CategorySpending] = []
    daily_trend: List[TrendPoint] = []
    weekly_trend: List[TrendPoint] = []
    monthly_trend: List[TrendPoint] = []
    top_recent_expenses: List[ExpenseRead] = []
    top_largest_expenses: List[ExpenseRead] = []
    financial_health_score: int = 100
    burn_rate_daily: float = 0.0
    projected_monthly_spend: float = 0.0
