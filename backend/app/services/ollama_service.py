import requests
import time
from typing import Tuple
from app.core.config import settings
from app.core.logging import ai_logger, error_logger


class OllamaService:

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    def is_available(self) -> bool:
        """Check if Ollama local server is running."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def is_model_available(self) -> bool:
        """Check if the configured model is pulled and available locally."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return any(self.model in m for m in models)
            return False
        except Exception:
            return False

    def generate_response(self, system_prompt: str, user_prompt: str) -> Tuple[str, bool, float]:
        """
        Query local Ollama instance with Llama 3.
        Returns Tuple[response_text, is_fallback, processing_time_ms].
        """
        start_time = time.time()
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9
            }
        }

        try:
            ai_logger.info(f"Sending request to Ollama ({self.model})...")
            response = requests.post(url, json=payload, timeout=self.timeout)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "").strip()
                ai_logger.info(f"Ollama response received in {elapsed_ms}ms")
                return answer, False, elapsed_ms

            elif response.status_code == 404:
                # Model not pulled yet — provide a specific "pull the model" message
                error_logger.error(f"Ollama model '{self.model}' not found (404). Pull it first.")
                return self._model_not_found_message(), True, elapsed_ms
            else:
                error_logger.error(f"Ollama returned HTTP status {response.status_code}: {response.text}")
                return self._fallback_message(), True, elapsed_ms

        except requests.exceptions.Timeout:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            error_logger.error(f"Ollama request timed out after {self.timeout}s")
            return (
                "**AI Timeout**: The Ollama server took too long to respond. "
                "Try asking a shorter question or verify your machine resources.",
                True,
                elapsed_ms
            )
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            error_logger.error(f"Failed to connect to local Ollama server: {str(e)}")
            return self._fallback_message(), True, elapsed_ms

    def _fallback_message(self) -> str:
        return (
            "**Local Ollama Server Unavailable**\n\n"
            "The AI Financial Assistant requires Ollama running locally.\n\n"
            "**Quick Setup:**\n"
            f"1. Install Ollama from https://ollama.com\n"
            f"2. Open a terminal and run: ollama pull {self.model}\n"
            f"3. Then start the model: ollama run {self.model}\n"
            "4. Refresh this page and ask your financial questions again!"
        )

    def _model_not_found_message(self) -> str:
        return (
            f"**Model '{self.model}' Not Found in Ollama**\n\n"
            f"Ollama is running but the {self.model} model has not been downloaded yet.\n\n"
            "**Fix this in one command:**\n"
            f"Open a terminal and run: ollama run {self.model}\n\n"
            "This will download the model (~4GB) and start it. "
            "Then refresh this page and ask your question again!"
        )


ollama_service = OllamaService()
