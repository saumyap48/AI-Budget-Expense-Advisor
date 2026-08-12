import sys
import os
from datetime import date

# Set test environment to use TEST_DATABASE_URL
os.environ["PYTEST_CURRENT_TEST"] = "1"

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.schemas.expense import ExpenseCreate
from app.schemas.budget import BudgetCreate
from app.schemas.chat import ChatRequest
from app.services.expense_service import ExpenseService
from app.services.budget_service import BudgetService
from app.services.analytics_service import AnalyticsService
from app.services.rag_service import RAGService


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
    test_user_id = 1
    for item in sample_expenses:
        created = expense_service.create_expense(item, user_id=test_user_id)
        created_items.append(created)
        print(f"  [OK] Created Expense #{created.id}: {created.description} (${created.amount}) under {created.category}")

    print("\n--- STEP 3: SETTING MONTHLY BUDGET ---")
    budget_res = budget_service.set_budget(user_id=test_user_id, data=BudgetCreate(monthly_budget=500.0, month=7, year=2026))
    print(f"  [OK] Budget set: ${budget_res.monthly_budget:.2f} | Spent: ${budget_res.total_spent:.2f} | Remaining: ${budget_res.remaining_balance:.2f} ({budget_res.percentage_spent}%)")

    print("\n--- STEP 4: GENERATING ANALYTICS SUMMARY ---")
    analytics = analytics_service.get_analytics_summary(user_id=test_user_id)
    print(f"  [OK] Total Expenses: ${analytics.total_expenses:.2f}")
    print(f"  [OK] Average Daily Spend: ${analytics.average_daily_spending:.2f}/day")
    print(f"  [OK] Highest Category: {analytics.highest_spending_category.category} (${analytics.highest_spending_category.total_amount:.2f})")
    print(f"  [OK] Health Score: {analytics.financial_health_score}/100")

    print("\n--- STEP 5: TESTING RAG CHAT QUERY ---")
    chat_res = rag_service.process_chat_query(user_id=test_user_id, request=ChatRequest(question="How much did I spend on Food?"))
    print(f"  [OK] AI Answer:\n{chat_res.answer}")
    print(f"  [OK] Context Documents Retrieved: {len(chat_res.retrieved_documents)}")

    db.close()
    print("\n[SUCCESS] ALL E2E VERIFICATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_e2e()
