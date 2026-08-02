from typing import Optional
from sqlalchemy.orm import Session
from app.models.budget import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):

    def __init__(self, db: Session):
        super().__init__(Budget, db)

    def get_by_month_year(self, user_id: int, month: int, year: int) -> Optional[Budget]:
        return self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year
        ).first()

    def set_or_update_budget(self, user_id: int, month: int, year: int, monthly_budget: float) -> Budget:
        existing = self.get_by_month_year(user_id, month, year)
        if existing:
            existing.monthly_budget = monthly_budget
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            budget = Budget(user_id=user_id, monthly_budget=monthly_budget, month=month, year=year)
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            return budget
