import urllib.request, json, sys

BASE = "http://localhost:8000"

def hit(method, path, data=None):
    url = BASE + path
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = json.loads(r.read())
            success = body.get("success", "?")
            msg = body.get("message", "")[:60]
            print(f"  [{r.status}] {method} {path}  -> success={success}  {msg}")
            return body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        print(f"  [{e.code}] {method} {path}  -> ERROR: {body.get('message','')}")
        return None
    except Exception as e:
        print(f"  [FAIL] {method} {path}  -> EXCEPTION: {e}")
        return None

print("=" * 65)
print("API ENDPOINT VERIFICATION SUITE")
print("=" * 65)

print("\n[1] HEALTH CHECK")
hit('GET', '/api/v1/health')

print("\n[2] EXPENSES LIST")
hit('GET', '/api/v1/expenses')

print("\n[3] CREATE EXPENSE")
r = hit('POST', '/api/v1/expenses', {
    'amount': 25.0,
    'category': 'Food',
    'description': 'API Test Coffee',
    'date': '2026-08-01',
    'payment_method': 'Cash'
})

new_id = None
if r and r.get('data'):
    new_id = r['data']['id']

print("\n[4] GET EXPENSE BY ID")
if new_id:
    hit('GET', f'/api/v1/expenses/{new_id}')

print("\n[5] UPDATE EXPENSE")
if new_id:
    hit('PUT', f'/api/v1/expenses/{new_id}', {'amount': 30.0, 'description': 'Updated API Coffee'})

print("\n[6] DELETE EXPENSE")
if new_id:
    hit('DELETE', f'/api/v1/expenses/{new_id}')

print("\n[7] SET BUDGET")
hit('POST', '/api/v1/budgets', {'monthly_budget': 600.0, 'month': 8, 'year': 2026})

print("\n[8] GET CURRENT BUDGET")
hit('GET', '/api/v1/budgets/current')

print("\n[9] GET ANALYTICS")
hit('GET', '/api/v1/analytics')

print("\n[10] AI CHAT (with Ollama fallback)")
hit('POST', '/api/v1/chat', {'question': 'What are my biggest expenses?'})

print("\n[11] VALIDATION ERROR TEST (negative amount)")
hit('POST', '/api/v1/expenses', {'amount': -10.0, 'category': 'Food', 'description': 'Bad', 'date': '2026-08-01'})

print("\n[12] NOT FOUND TEST")
hit('GET', '/api/v1/expenses/99999')

print("\n" + "=" * 65)
print("ALL ENDPOINT TESTS COMPLETE")
print("=" * 65)
