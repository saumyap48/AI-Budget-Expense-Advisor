from datetime import datetime
from sqlalchemy.orm import Session
from app.schemas.budget import BudgetCreate, BudgetStatus
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.utils.datetime_utils import get_current_month_year


class BudgetService:

    def __init__(self, db: Session):
        self.budget_repo = BudgetRepository(db)
        self.expense_repo = ExpenseRepository(db)

    def get_current_budget_status(self, user_id: int, month: int = None, year: int = None) -> BudgetStatus:
        if not month or not year:
            month, year = get_current_month_year()

        budget = self.budget_repo.get_by_month_year(user_id, month, year)
        monthly_budget = float(budget.monthly_budget) if budget else 0.0
        budget_id = budget.id if budget else None

        total_spent = self.expense_repo.get_monthly_spent(user_id, month, year)
        remaining_balance = monthly_budget - total_spent if monthly_budget > 0 else 0.0

        percentage_spent = (total_spent / monthly_budget * 100.0) if monthly_budget > 0 else 0.0
        percentage_spent = round(percentage_spent, 2)

        is_warning = percentage_spent >= 80.0 and percentage_spent <= 100.0
        is_exceeded = percentage_spent > 100.0

        if is_exceeded:
            status_level = "exceeded"
            message = f"[ALERT] You have exceeded your budget by ${abs(remaining_balance):.2f} ({percentage_spent}%)!"
        elif is_warning:
            status_level = "warning"
            message = f"[WARNING] You have used {percentage_spent}% of your monthly budget!"
        elif monthly_budget > 0:
            status_level = "normal"
            message = f"[OK] You have ${remaining_balance:.2f} remaining in your budget."
        else:
            status_level = "not_set"
            message = "[INFO] No budget set for this month. Set a budget to track spending limits."

        return BudgetStatus(
            id=budget_id,
            monthly_budget=monthly_budget,
            month=month,
            year=year,
            total_spent=round(total_spent, 2),
            remaining_balance=round(remaining_balance, 2),
            percentage_spent=percentage_spent,
            is_warning=is_warning,
            is_exceeded=is_exceeded,
            status_level=status_level,
            message=message
        )

    def set_budget(self, user_id: int, data: BudgetCreate) -> BudgetStatus:
        self.budget_repo.set_or_update_budget(
            user_id=user_id,
            month=data.month,
            year=data.year,
            monthly_budget=data.monthly_budget
        )
        return self.get_current_budget_status(user_id=user_id, month=data.month, year=data.year)
