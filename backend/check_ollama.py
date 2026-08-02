import requests, json

print("=== CHECKING CURRENT OLLAMA MODELS ===")
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    print("Status:", r.status_code)
    data = r.json()
    models = data.get("models", [])
    print(f"Total Models Found: {len(models)}")
    for m in models:
        print(f" - Name: {m.get('name')}, Size: {m.get('size', 0)/1e9:.2f}GB")
except Exception as e:
    print("Error querying Ollama:", e)
