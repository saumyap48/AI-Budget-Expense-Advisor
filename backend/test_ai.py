import urllib.request, json

BASE = "http://localhost:8000"

def hit(method, path, data=None):
    url = BASE + path
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
            return r.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        return e.code, body
    except Exception as e:
        return 0, {"error": str(e)}

print("=" * 60)
print("OLLAMA AI CHAT LIVE TEST (llama3.2)")
print("=" * 60)

# First check health to confirm model config
status, data = hit('GET', '/api/v1/health')
print(f"\n[{status}] /api/v1/health")
if data.get('data'):
    print(f"  DB:     {data['data'].get('database')}")
    print(f"  Ollama: {data['data'].get('ollama_llm')}")

# Test AI chat
print("\n--- SENDING CHAT QUESTION TO llama3.2 ---")
question = "How much did I spend on Food? Give me a brief summary."
status, data = hit('POST', '/api/v1/chat', {"question": question})
print(f"[{status}] POST /api/v1/chat")

if data.get('success') and data.get('data'):
    d = data['data']
    print(f"  Model Used:     {d.get('model_used')}")
    print(f"  Is Fallback:    {d.get('is_fallback')}")
    print(f"  Docs Retrieved: {len(d.get('retrieved_documents', []))}")
    print(f"  Response Time:  {d.get('processing_time_ms')}ms")
    print(f"\n  AI ANSWER:\n  {'-'*50}")
    answer = d.get('answer', '')
    # Print safely (strip any non-ascii for windows terminal)
    safe_answer = answer.encode('ascii', errors='replace').decode('ascii')
    print(f"  {safe_answer[:1000]}")
else:
    print(f"  Response: {data}")

print("\n" + "=" * 60)
print("OLLAMA AI TEST COMPLETE")
print("=" * 60)
