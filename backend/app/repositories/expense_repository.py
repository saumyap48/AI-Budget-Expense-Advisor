from datetime import date as DateType
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, extract
from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):

    def __init__(self, db: Session):
        super().__init__(Expense, db)

    def get_by_id_and_user(self, id: int, user_id: int) -> Optional[Expense]:
        return self.db.query(Expense).filter(
            Expense.id == id,
            Expense.user_id == user_id
        ).first()

    def get_filtered(
        self,
        user_id: int,
        category: Optional[str] = None,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search_query: Optional[str] = None,
        sort_by: str = "date",
        order: str = "desc",
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Expense], int]:
        query = self.db.query(Expense).filter(Expense.user_id == user_id)

        if category:
            query = query.filter(Expense.category == category)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        if min_amount is not None:
            query = query.filter(Expense.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Expense.amount <= max_amount)
        if search_query:
            pattern = f"%{search_query}%"
            query = query.filter(
                (Expense.description.ilike(pattern)) |
                (Expense.notes.ilike(pattern)) |
                (Expense.category.ilike(pattern))
            )

        total_records = query.count()

        # Sorting
        sort_column = getattr(Expense, sort_by, Expense.date)
        if order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        return items, total_records

    def get_category_totals(
        self,
        user_id: int,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None
    ) -> List[Tuple[str, float, int]]:
        query = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count")
        ).filter(Expense.user_id == user_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        return query.group_by(Expense.category).order_by(desc("total")).all()

    def get_daily_trends(
        self,
        user_id: int,
        start_date: Optional[DateType] = None,
        end_date: Optional[DateType] = None
    ) -> List[Tuple[DateType, float]]:
        query = self.db.query(
            Expense.date,
            func.sum(Expense.amount).label("total")
        ).filter(Expense.user_id == user_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        return query.group_by(Expense.date).order_by(asc(Expense.date)).all()

    def get_monthly_spent(self, user_id: int, month: int, year: int) -> float:
        result = self.db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        ).scalar()

        return float(result) if result else 0.0

    def get_top_expenses(self, user_id: int, limit: int = 5, sort_by_amount: bool = False) -> List[Expense]:
        query = self.db.query(Expense).filter(Expense.user_id == user_id)
        if sort_by_amount:
            query = query.order_by(desc(Expense.amount))
        else:
            query = query.order_by(desc(Expense.date), desc(Expense.id))
        return query.limit(limit).all()

    def update_expense_user(self, id: int, user_id: int, data: Dict[str, Any]) -> Optional[Expense]:
        expense = self.get_by_id_and_user(id, user_id)
        if not expense:
            return None
        for key, value in data.items():
            if value is not None and hasattr(expense, key):
                setattr(expense, key, value)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete_expense_user(self, id: int, user_id: int) -> bool:
        expense = self.get_by_id_and_user(id, user_id)
        if not expense:
            return False
        self.db.delete(expense)
        self.db.commit()
        return True
