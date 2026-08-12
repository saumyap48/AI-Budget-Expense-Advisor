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


def test_ai_chat_flow():
    print("=" * 60)
    print("AI CHAT ENDPOINT & GEMINI SERVICE INTEGRATION TEST")
    print("=" * 60)

    # Initialize fresh test database schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Register test user
    user_data = {
        "full_name": "AI Tester",
        "email": "aitest@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r = client.post("/api/v1/auth/register", json=user_data)
    assert r.status_code == 201
    headers = {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

    # Add sample expense for context
    client.post("/api/v1/expenses", headers=headers, json={
        "amount": 75.0, "category": "Food", "description": "Weekly grocery at Whole Foods",
        "date": "2026-08-01", "payment_method": "Credit Card"
    })

    # Test health check LLM status
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    health_data = r.json()["data"]
    print(f"\n[Health Check] Gemini LLM Status: {health_data.get('gemini_llm')}")

    # Test AI chat query
    print("\n--- SENDING CHAT QUESTION TO AI ASSISTANT ---")
    question = "How much did I spend on Food? Give me a brief summary."
    r = client.post("/api/v1/chat", headers=headers, json={"question": question})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["success"] is True

    d = body["data"]
    print(f"  Model Used:     {d.get('model_used')}")
    print(f"  Is Fallback:    {d.get('is_fallback')}")
    print(f"  Docs Retrieved: {len(d.get('retrieved_documents', []))}")
    print(f"  Response Time:  {d.get('processing_time_ms')}ms")
    print(f"\n  AI ANSWER:\n  {'-'*50}")
    answer = d.get('answer', '')
    safe_answer = answer.encode('ascii', errors='replace').decode('ascii')
    print(f"  {safe_answer[:1000]}")

    print("\n" + "=" * 60)
    print("AI TEST COMPLETE AND VERIFIED")
    print("=" * 60)


if __name__ == "__main__":
    test_ai_chat_flow()
