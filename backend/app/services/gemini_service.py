import time
from typing import Tuple
import google.generativeai as genai
from backend.app.core.config import settings
from backend.app.core.logging import ai_logger, error_logger


class GeminiService:

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.9,
            )
        )

    @property
    def model(self) -> str:
        return self.model_name

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(settings.GEMINI_API_KEY)

    def generate_response(self, system_prompt: str, user_prompt: str) -> Tuple[str, bool, float]:
        """
        Query Gemini API.
        Returns Tuple[response_text, is_fallback, processing_time_ms].
        """
        start_time = time.time()

        try:
            ai_logger.info(f"Sending request to Gemini ({self.model_name})...")

            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self._model.generate_content(full_prompt)

            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            answer = response.text.strip()
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
