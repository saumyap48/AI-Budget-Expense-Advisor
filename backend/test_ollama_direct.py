import requests

print("Testing all installed models with /api/generate...\n")

models = ["llama3.2:latest", "qwen2.5:latest", "nomic-embed-text:latest"]

for model in models:
    print(f"Testing: {model}")
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": "Say one word.", "stream": False},
            timeout=60)
        if r.status_code == 200:
            answer = r.json().get("response", "")[:80]
            print(f"  [OK 200] Response: {answer!r}")
        else:
            print(f"  [{r.status_code}] Error: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] {e}")
    print()
