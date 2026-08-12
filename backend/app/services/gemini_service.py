import time
from typing import Tuple
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.logging import ai_logger, error_logger


class GeminiService:

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        if settings.GEMINI_API_KEY:
            try:
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                error_logger.error(f"Failed to initialize Gemini Client: {e}")

    @property
    def model(self) -> str:
        return self.model_name

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(settings.GEMINI_API_KEY)

    def generate_response(self, system_prompt: str, user_prompt: str) -> Tuple[str, bool, float]:
        """
        Query Gemini API using google.genai SDK.
        Returns Tuple[response_text, is_fallback, processing_time_ms].
        """
        start_time = time.time()

        try:
            if not self._client:
                if settings.GEMINI_API_KEY:
                    self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
                else:
                    raise ValueError("GEMINI_API_KEY is not configured.")

            ai_logger.info(f"Sending request to Gemini ({self.model_name})...")

            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.9,
                ),
            )

            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            answer = response.text.strip() if (response and response.text) else ""
            ai_logger.info(f"Gemini response received in {elapsed_ms}ms")
            return answer, False, elapsed_ms

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            error_logger.error(f"Gemini API request failed: {str(e)}")
            return self._fallback_message(str(e)), True, elapsed_ms

    def _fallback_message(self, error: str = "") -> str:
        return (
            "**Gemini AI Unavailable**\n\n"
            "Could not reach the Gemini API. Please check your API key and network connection.\n\n"
            f"Error details: {error}" if error else
            "**Gemini AI Unavailable**\n\n"
            "Could not reach the Gemini API. Please check your API key and network connection."
        )


gemini_service = GeminiService()
