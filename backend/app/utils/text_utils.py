from backend.app.models.expense import Expense


def build_expense_document(expense: Expense) -> str:
    """Convert expense object into human-readable document string for vector indexing."""
    date_str = expense.date.strftime("%B %d, %Y") if hasattr(expense.date, "strftime") else str(expense.date)
    method_str = f" via {expense.payment_method}" if getattr(expense, "payment_method", None) else ""
    notes_str = f" Notes: {expense.notes}." if getattr(expense, "notes", None) else ""

    return (
        f"Spent ${expense.amount:.2f} on {expense.description} "
        f"under {expense.category} category on {date_str}{method_str}.{notes_str}"
    )
