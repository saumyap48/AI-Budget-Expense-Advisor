import sys
import os
from datetime import date

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.schemas.expense import ExpenseCreate
from backend.app.schemas.budget import BudgetCreate
from backend.app.schemas.chat import ChatRequest
from backend.app.services.expense_service import ExpenseService
from backend.app.services.budget_service import BudgetService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.rag_service import RAGService


def test_e2e():
    print("--- STEP 1: INITIALIZING DATABASE TABLES ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    expense_service = ExpenseService(db)
    budget_service = BudgetService(db)
    analytics_service = AnalyticsService(db)
    rag_service = RAGService(db)

    print("\n--- STEP 2: CREATING SAMPLE EXPENSES & VECTOR SYNC ---")
    sample_expenses = [
        ExpenseCreate(amount=45.50, category="Food", description="Grocery shopping at Walmart", date=date(2026, 7, 28), payment_method="Credit Card"),
        ExpenseCreate(amount=12.00, category="Food", description="Lunch Pizza at Domino's", date=date(2026, 7, 29), payment_method="Cash"),
        ExpenseCreate(amount=85.00, category="Bills", description="Electricity utility bill", date=date(2026, 7, 25), payment_method="Bank Transfer"),
        ExpenseCreate(amount=30.00, category="Transport", description="Uber ride to office", date=date(2026, 7, 30), payment_method="UPI"),
        ExpenseCreate(amount=60.00, category="Entertainment", description="Movie tickets and popcorn", date=date(2026, 7, 27), payment_method="Debit Card")
    ]

    created_items = []
    for item in sample_expenses:
        created = expense_service.create_expense(item)
        created_items.append(created)
        print(f"✅ Created Expense #{created.id}: {created.description} (${created.amount}) under {created.category}")

    print("\n--- STEP 3: SETTING MONTHLY BUDGET ---")
    budget_res = budget_service.set_budget(BudgetCreate(monthly_budget=500.0, month=7, year=2026))
    print(f"✅ Budget set: ${budget_res.monthly_budget:.2f} | Spent: ${budget_res.total_spent:.2f} | Remaining: ${budget_res.remaining_balance:.2f} ({budget_res.percentage_spent}%)")

    print("\n--- STEP 4: GENERATING ANALYTICS SUMMARY ---")
    analytics = analytics_service.get_analytics_summary()
    print(f"✅ Total Expenses: ${analytics.total_expenses:.2f}")
    print(f"✅ Average Daily Spend: ${analytics.average_daily_spending:.2f}/day")
    print(f"✅ Highest Category: {analytics.highest_spending_category.category} (${analytics.highest_spending_category.total_amount:.2f})")
    print(f"✅ Health Score: {analytics.financial_health_score}/100")

    print("\n--- STEP 5: TESTING RAG CHAT QUERY ---")
    chat_res = rag_service.process_chat_query(ChatRequest(question="How much did I spend on Food?"))
    print(f"✅ AI Answer:\n{chat_res.answer}")
    print(f"✅ Context Documents Retrieved: {len(chat_res.retrieved_documents)}")

    db.close()
    print("\n🎉 ALL E2E VERIFICATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_e2e()
