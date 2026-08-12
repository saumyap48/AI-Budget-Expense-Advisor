import os
import sys

# Ensure test environment to use TEST_DATABASE_URL
os.environ["PYTEST_CURRENT_TEST"] = "1"

# Add project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

client = TestClient(app)


def test_full_api_suite():
    print("=" * 65)
    print("FASTAPI COMPREHENSIVE ENDPOINT VERIFICATION SUITE")
    print("=" * 65)

    # Initialize fresh test database schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("\n[0] Test database schema initialized.")

    # 1. Health Check
    print("\n[1] HEALTH CHECK")
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    body = r.json()
    assert body["success"] is True
    print(f"  [200] GET /api/v1/health -> DB: {body['data']['database']} | Gemini: {body['data']['gemini_llm']}")

    # 2. Root Endpoint
    print("\n[2] ROOT ENDPOINT")
    r = client.get("/")
    assert r.status_code == 200
    print(f"  [200] GET / -> status: {r.json()['status']}")

    # 3. Unauthenticated Access (401 Check)
    print("\n[3] UNAUTHENTICATED ACCESS CHECKS")
    r = client.get("/api/v1/expenses")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print("  [401] GET /api/v1/expenses -> Unauthorized blocked successfully")

    r = client.get("/api/v1/budgets/current")
    assert r.status_code == 401
    print("  [401] GET /api/v1/budgets/current -> Unauthorized blocked successfully")

    # 4. User Registration & Authentication
    print("\n[4] USER REGISTRATION & LOGIN")
    user1_data = {
        "full_name": "API Test User 1",
        "email": "user1@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r = client.post("/api/v1/auth/register", json=user1_data)
    assert r.status_code == 201, f"Register failed: {r.text}"
    token1 = r.json()["data"]["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    print("  [201] POST /api/v1/auth/register -> User 1 registered successfully")

    r = client.get("/api/v1/auth/me", headers=headers1)
    assert r.status_code == 200
    assert r.json()["data"]["email"] == "user1@example.com"
    print(f"  [200] GET /api/v1/auth/me -> Profile retrieved: {r.json()['data']['full_name']}")

    # 5. Create Expense
    print("\n[5] CREATE EXPENSE")
    expense_payload = {
        "amount": 25.50,
        "category": "Food",
        "description": "Coffee and Snacks",
        "date": "2026-08-01",
        "payment_method": "Cash",
        "notes": "Morning team refresh"
    }
    r = client.post("/api/v1/expenses", headers=headers1, json=expense_payload)
    assert r.status_code == 201, f"Create expense failed: {r.text}"
    exp_id = r.json()["data"]["id"]
    print(f"  [201] POST /api/v1/expenses -> Created Expense #{exp_id} ($25.50 Food)")

    # 6. List Expenses
    print("\n[6] LIST EXPENSES")
    r = client.get("/api/v1/expenses", headers=headers1)
    assert r.status_code == 200
    items = r.json()["data"]
    assert len(items) == 1
    assert items[0]["id"] == exp_id
    print(f"  [200] GET /api/v1/expenses -> Listed {len(items)} expense(s)")

    # 7. Get Expense By ID
    print("\n[7] GET EXPENSE BY ID")
    r = client.get(f"/api/v1/expenses/{exp_id}", headers=headers1)
    assert r.status_code == 200
    assert r.json()["data"]["amount"] == 25.50
    print(f"  [200] GET /api/v1/expenses/{exp_id} -> Retrieved successfully")

    # 8. Update Expense
    print("\n[8] UPDATE EXPENSE")
    update_payload = {"amount": 30.00, "description": "Updated Coffee and Pastry"}
    r = client.put(f"/api/v1/expenses/{exp_id}", headers=headers1, json=update_payload)
    assert r.status_code == 200
    assert r.json()["data"]["amount"] == 30.00
    assert r.json()["data"]["description"] == "Updated Coffee and Pastry"
    print(f"  [200] PUT /api/v1/expenses/{exp_id} -> Updated amount to $30.00")

    # 9. Set & Get Budget
    print("\n[9] BUDGET ENDPOINTS")
    budget_payload = {"monthly_budget": 500.0, "month": 8, "year": 2026}
    r = client.post("/api/v1/budgets", headers=headers1, json=budget_payload)
    assert r.status_code == 201
    assert r.json()["data"]["monthly_budget"] == 500.0
    print("  [201] POST /api/v1/budgets -> Set budget to $500.00")

    r = client.get("/api/v1/budgets/current?month=8&year=2026", headers=headers1)
    assert r.status_code == 200
    b_status = r.json()["data"]
    assert b_status["total_spent"] == 30.00
    assert b_status["remaining_balance"] == 470.00
    print(f"  [200] GET /api/v1/budgets/current -> Spent: ${b_status['total_spent']} | Remaining: ${b_status['remaining_balance']}")

    # 10. Analytics Summary
    print("\n[10] ANALYTICS ENDPOINT")
    r = client.get("/api/v1/analytics", headers=headers1)
    assert r.status_code == 200
    analytics_data = r.json()["data"]
    assert analytics_data["total_expenses"] == 30.00
    assert analytics_data["total_count"] == 1
    print(f"  [200] GET /api/v1/analytics -> Total Expenses: ${analytics_data['total_expenses']} | Score: {analytics_data['financial_health_score']}")

    # 11. AI RAG Chat
    print("\n[11] AI RAG CHAT ENDPOINT")
    chat_payload = {"question": "How much did I spend on Food?"}
    r = client.post("/api/v1/chat", headers=headers1, json=chat_payload)
    assert r.status_code == 200
    chat_data = r.json()["data"]
    assert "answer" in chat_data
    print(f"  [200] POST /api/v1/chat -> AI Model ({chat_data['model_used']}) answered query")

    # 12. Multi-User Isolation Checks
    print("\n[12] MULTI-USER ISOLATION CHECKS")
    user2_data = {
        "full_name": "API Test User 2",
        "email": "user2@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r = client.post("/api/v1/auth/register", json=user2_data)
    assert r.status_code == 201
    headers2 = {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

    # User 2 cannot list User 1's expenses
    r = client.get("/api/v1/expenses", headers=headers2)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 0
    print("  User 2 GET /api/v1/expenses -> 0 expenses found (Isolated)")

    # User 2 cannot access User 1's expense by ID (404)
    r = client.get(f"/api/v1/expenses/{exp_id}", headers=headers2)
    assert r.status_code == 404
    print("  User 2 GET User 1's expense -> 404 Not Found (Isolated)")

    # User 2 cannot update User 1's expense (404)
    r = client.put(f"/api/v1/expenses/{exp_id}", headers=headers2, json={"amount": 999.00})
    assert r.status_code == 404
    print("  User 2 PUT User 1's expense -> 404 Not Found (Isolated)")

    # User 2 cannot delete User 1's expense (404)
    r = client.delete(f"/api/v1/expenses/{exp_id}", headers=headers2)
    assert r.status_code == 404
    print("  User 2 DELETE User 1's expense -> 404 Not Found (Isolated)")

    # 13. Delete Expense by Owner
    print("\n[13] DELETE EXPENSE BY OWNER")
    r = client.delete(f"/api/v1/expenses/{exp_id}", headers=headers1)
    assert r.status_code == 200
    print(f"  [200] DELETE /api/v1/expenses/{exp_id} -> Deleted successfully")

    # 14. Validation Error & Not Found Tests
    print("\n[14] VALIDATION & NOT FOUND TESTS")
    # Invalid expense category
    r = client.post("/api/v1/expenses", headers=headers1, json={
        "amount": 10.0, "category": "InvalidCat", "description": "Test", "date": "2026-08-01"
    })
    assert r.status_code == 422 or r.status_code == 400
    print("  Invalid category rejected with 422/400 (PASSED)")

    # Negative expense amount
    r = client.post("/api/v1/expenses", headers=headers1, json={
        "amount": -50.0, "category": "Food", "description": "Test", "date": "2026-08-01"
    })
    assert r.status_code == 422 or r.status_code == 400
    print("  Negative amount rejected with 422/400 (PASSED)")

    # Non-existent ID lookup
    r = client.get("/api/v1/expenses/99999", headers=headers1)
    assert r.status_code == 404
    print("  Non-existent ID returns 404 (PASSED)")

    print("\n" + "=" * 65)
    print("ALL API ENDPOINT VERIFICATION SUITE TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    test_full_api_suite()
