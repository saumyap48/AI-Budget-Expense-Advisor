from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.schemas.analytics import AnalyticsSummary, CategorySpending, TrendPoint
from app.schemas.expense import ExpenseRead
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.budget_repository import BudgetRepository
from app.utils.datetime_utils import get_current_month_year, get_month_date_range


class AnalyticsService:

    def __init__(self, db: Session):
        self.expense_repo = ExpenseRepository(db)
        self.budget_repo = BudgetRepository(db)

    def get_analytics_summary(self, user_id: int) -> AnalyticsSummary:
        month, year = get_current_month_year()
        start_date, end_date = get_month_date_range(year, month)

        # Total expenses & count
        all_expenses, total_count = self.expense_repo.get_filtered(user_id=user_id, limit=1000)
        total_expenses = sum(e.amount for e in all_expenses)

        # Average daily spending in current month
        days_in_month = (date.today() - start_date).days + 1 if date.today().month == month else 30
        days_in_month = max(1, days_in_month)
        current_month_spent = self.expense_repo.get_monthly_spent(user_id, month, year)
        average_daily = current_month_spent / days_in_month

        # Category totals
        raw_categories = self.expense_repo.get_category_totals(user_id=user_id)
        category_breakdown: List[CategorySpending] = []

        for cat, total, count in raw_categories:
            pct = (total / total_expenses * 100.0) if total_expenses > 0 else 0.0
            category_breakdown.append(CategorySpending(
                category=cat,
                total_amount=round(total, 2),
                percentage=round(pct, 1),
                count=count
            ))

        highest_category = category_breakdown[0] if category_breakdown else None
        lowest_category = category_breakdown[-1] if category_breakdown else None

        # Trends
        raw_daily = self.expense_repo.get_daily_trends(user_id=user_id, start_date=start_date, end_date=end_date)
        daily_trend = [
            TrendPoint(period=d.strftime("%Y-%m-%d"), amount=round(amt, 2))
            for d, amt in raw_daily
        ]

        # Top recent and largest expenses
        top_recent_orm = self.expense_repo.get_top_expenses(user_id=user_id, limit=5, sort_by_amount=False)
        top_largest_orm = self.expense_repo.get_top_expenses(user_id=user_id, limit=5, sort_by_amount=True)

        top_recent = [ExpenseRead.from_orm(e) for e in top_recent_orm]
        top_largest = [ExpenseRead.from_orm(e) for e in top_largest_orm]

        # Health score math
        budget = self.budget_repo.get_by_month_year(user_id, month, year)
        health_score = 100
        if budget and budget.monthly_budget > 0:
            spent_pct = (current_month_spent / budget.monthly_budget) * 100
            if spent_pct > 100:
                health_score = max(30, int(100 - (spent_pct - 100) * 1.5))
            elif spent_pct > 80:
                health_score = int(100 - (spent_pct - 80))

        return AnalyticsSummary(
            total_expenses=round(total_expenses, 2),
            total_count=total_count,
            average_daily_spending=round(average_daily, 2),
            highest_spending_category=highest_category,
            lowest_spending_category=lowest_category,
            category_breakdown=category_breakdown,
            daily_trend=daily_trend,
            weekly_trend=[],
            monthly_trend=[],
            top_recent_expenses=top_recent,
            top_largest_expenses=top_largest,
            financial_health_score=health_score,
            burn_rate_daily=round(average_daily, 2),
            projected_monthly_spend=round(average_daily * 30, 2)
        )
