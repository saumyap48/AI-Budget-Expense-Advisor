from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.expense import Expense
from backend.app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseFilter
from backend.app.repositories.expense_repository import ExpenseRepository
from backend.app.services.chroma_service import chroma_service
from backend.app.core.exceptions import NotFoundException
from backend.app.core.security import sanitize_input


class ExpenseService:

    def __init__(self, db: Session):
        self.repository = ExpenseRepository(db)

    def list_expenses(
        self,
        user_id: int,
        filters: ExpenseFilter,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "date",
        order: str = "desc"
    ) -> Tuple[List[Expense], int]:
        return self.repository.get_filtered(
            user_id=user_id,
            category=filters.category,
            start_date=filters.start_date,
            end_date=filters.end_date,
            min_amount=filters.min_amount,
            max_amount=filters.max_amount,
            search_query=filters.q,
            sort_by=sort_by,
            order=order,
            page=page,
            limit=limit
        )

    def get_expense(self, expense_id: int, user_id: int) -> Expense:
        expense = self.repository.get_by_id_and_user(expense_id, user_id)
        if not expense:
            raise NotFoundException(f"Expense with ID {expense_id} not found")
        return expense

    def create_expense(self, data: ExpenseCreate, user_id: int) -> Expense:
        sanitized_description = sanitize_input(data.description)
        sanitized_notes = sanitize_input(data.notes) if data.notes else None

        expense_dict = data.dict()
        expense_dict["user_id"] = user_id
        expense_dict["description"] = sanitized_description
        expense_dict["notes"] = sanitized_notes

        expense = self.repository.create(expense_dict)

        # Sync with ChromaDB vector store
        chroma_service.add_or_update_expense(expense)

        return expense

    def update_expense(self, expense_id: int, user_id: int, data: ExpenseUpdate) -> Expense:
        self.get_expense(expense_id, user_id)  # Assures expense belongs to user

        update_data = data.dict(exclude_unset=True)
        if "description" in update_data and update_data["description"]:
            update_data["description"] = sanitize_input(update_data["description"])
        if "notes" in update_data and update_data["notes"]:
            update_data["notes"] = sanitize_input(update_data["notes"])

        updated_expense = self.repository.update_expense_user(expense_id, user_id, update_data)

        # Sync updated expense with ChromaDB vector store
        if updated_expense:
            chroma_service.add_or_update_expense(updated_expense)

        return updated_expense

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        self.get_expense(expense_id, user_id)  # Raises NotFoundException if not exists
        success = self.repository.delete_expense_user(expense_id, user_id)
        if success:
            chroma_service.delete_expense(expense_id)
        return success
