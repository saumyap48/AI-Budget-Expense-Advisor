import os
import sys

# Ensure backend path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine

client = TestClient(app)

print("=" * 65)
print("AUTHENTICATION & MULTI-USER ISOLATION E2E TEST SUITE")
print("=" * 65)

# Step 0: Ensure DB tables exist
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("\n[0] Database tables initialized fresh.")

# Step 1: Unauthorized access test
print("\n[1] TEST UNAUTHORIZED ACCESS (NO TOKEN)")
res = client.get("/api/v1/expenses")
assert res.status_code == 401, f"Expected 401, got {res.status_code}"
print("  GET /api/v1/expenses -> 401 Unauthorized (PASSED)")

res = client.get("/api/v1/budgets/current")
assert res.status_code == 401, f"Expected 401, got {res.status_code}"
print("  GET /api/v1/budgets/current -> 401 Unauthorized (PASSED)")

res = client.get("/api/v1/analytics")
assert res.status_code == 401, f"Expected 401, got {res.status_code}"
print("  GET /api/v1/analytics -> 401 Unauthorized (PASSED)")

# Step 2: User A (Alice) Registration
print("\n[2] TEST USER A (ALICE) REGISTRATION")
alice_data = {
    "full_name": "Alice Johnson",
    "email": "alice@example.com",
    "password": "Password123!",
    "confirm_password": "Password123!"
}
res = client.post("/api/v1/auth/register", json=alice_data)
assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
alice_json = res.json()
alice_token = alice_json["data"]["access_token"]
alice_headers = {"Authorization": f"Bearer {alice_token}"}
print(f"  Alice registered successfully. Token length: {len(alice_token)}")

# Step 3: Duplicate Email Validation
print("\n[3] TEST DUPLICATE EMAIL REGISTRATION (BAD REQUEST)")
res = client.post("/api/v1/auth/register", json=alice_data)
assert res.status_code == 400, f"Expected 400, got {res.status_code}"
print("  Duplicate registration blocked with 400 Bad Request (PASSED)")

# Step 4: User A Login
print("\n[4] TEST USER A LOGIN")
res = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "Password123!"})
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
print("  Alice login successful (PASSED)")

# Step 5: Get Me (Current User Details)
print("\n[5] TEST GET ME (/api/v1/auth/me)")
res = client.get("/api/v1/auth/me", headers=alice_headers)
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
me = res.json()["data"]
assert me["email"] == "alice@example.com"
assert me["full_name"] == "Alice Johnson"
print(f"  Retrieved user profile: {me['full_name']} ({me['email']}) (PASSED)")

# Step 6: User A Creates Expenses & Set Budget
print("\n[6] USER A (ALICE) ADDS EXPENSES & SETS BUDGET")
res = client.post("/api/v1/expenses", headers=alice_headers, json={
    "amount": 120.0, "category": "Food", "description": "Alice Grocery Shopping",
    "date": "2026-08-01", "payment_method": "Credit Card"
})
assert res.status_code == 201
alice_exp_id = res.json()["data"]["id"]
print(f"  Alice created Expense #{alice_exp_id}: $120 Grocery")

res = client.post("/api/v1/budgets", headers=alice_headers, json={
    "monthly_budget": 500.0, "month": 8, "year": 2026
})
assert res.status_code == 201
print("  Alice set Monthly Budget: $500")

# Step 7: User B (Bob) Registration & Login
print("\n[7] USER B (BOB) REGISTRATION & LOGIN")
bob_data = {
    "full_name": "Bob Smith",
    "email": "bob@example.com",
    "password": "SecurePassword456!",
    "confirm_password": "SecurePassword456!"
}
res = client.post("/api/v1/auth/register", json=bob_data)
assert res.status_code == 201
bob_token = res.json()["data"]["access_token"]
bob_headers = {"Authorization": f"Bearer {bob_token}"}
print("  Bob registered successfully")

# Step 8: Multi-User Data Isolation Check
print("\n[8] TEST MULTI-USER DATA ISOLATION")

# Bob lists expenses -> should be EMPTY
res = client.get("/api/v1/expenses", headers=bob_headers)
assert res.status_code == 200
bob_expenses = res.json()["data"]
assert len(bob_expenses) == 0, f"Expected Bob expenses to be 0, but got {len(bob_expenses)}"
print("  Bob lists expenses -> 0 expenses found (Alice's data is isolated!) (PASSED)")

# Bob checks budget -> should be not set
res = client.get("/api/v1/budgets/current", headers=bob_headers)
assert res.status_code == 200
bob_budget = res.json()["data"]
assert bob_budget["monthly_budget"] == 0.0, "Expected Bob budget to be 0.0"
print("  Bob checks budget -> $0 budget (Alice's budget is isolated!) (PASSED)")

# Bob tries to access Alice's expense by ID -> 404 Not Found
res = client.get(f"/api/v1/expenses/{alice_exp_id}", headers=bob_headers)
assert res.status_code == 404, f"Expected 404, got {res.status_code}"
print(f"  Bob tries to access Alice's expense #{alice_exp_id} -> 404 Not Found (PASSED)")

# Bob adds his own expense
res = client.post("/api/v1/expenses", headers=bob_headers, json={
    "amount": 45.0, "category": "Entertainment", "description": "Bob Cinema Tickets",
    "date": "2026-08-01", "payment_method": "Cash"
})
assert res.status_code == 201
bob_exp_id = res.json()["data"]["id"]
print(f"  Bob created Expense #{bob_exp_id}: $45 Cinema")

# Alice lists expenses -> should contain ONLY Alice's expense
res = client.get("/api/v1/expenses", headers=alice_headers)
alice_expenses = res.json()["data"]
assert len(alice_expenses) == 1
assert alice_expenses[0]["description"] == "Alice Grocery Shopping"
print("  Alice lists expenses -> 1 expense found ('Alice Grocery Shopping') (PASSED)")

# Step 9: Analytics Isolation Check
print("\n[9] TEST ANALYTICS ISOLATION")
res = client.get("/api/v1/analytics", headers=alice_headers)
alice_analytics = res.json()["data"]
assert alice_analytics["total_expenses"] == 120.0

res = client.get("/api/v1/analytics", headers=bob_headers)
bob_analytics = res.json()["data"]
assert bob_analytics["total_expenses"] == 45.0
print("  Alice total expenses = $120.00 | Bob total expenses = $45.00 (PASSED)")

# Step 10: RAG AI Vector Search Isolation Check
print("\n[10] TEST AI RAG CONTEXT ISOLATION")
res = client.post("/api/v1/chat", headers=bob_headers, json={"question": "What did I spend money on?"})
assert res.status_code == 200
bob_rag_docs = res.json()["data"]["retrieved_documents"]
# Check that Bob's retrieved docs contain only Bob's items
for doc in bob_rag_docs:
    assert "Alice" not in doc["content"], f"Security Breach: Alice's context leaked to Bob! {doc}"
print("  Bob queries AI -> No Alice data present in retrieved vector context (PASSED)")

print("\n" + "=" * 65)
print("[SUCCESS] ALL AUTHENTICATION & MULTI-USER E2E TESTS PASSED!")
print("=" * 65)
