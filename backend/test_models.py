import requests

def test_models_direct():
    models_to_test = ["qwen3:4b", "gemma3:1b"]

    for m in models_to_test:
        print(f"\n--- Testing model: {m} ---")
        try:
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": m,
                "prompt": "Hello! Reply with 'OK'.",
                "stream": False
            }, timeout=5)
            print("Status Code:", r.status_code)
            if r.status_code == 200:
                print("Response:", r.json().get("response", "").strip())
            else:
                print("Error output:", r.text)
        except Exception as e:
            print("Exception:", e)


if __name__ == "__main__":
    test_models_direct()
