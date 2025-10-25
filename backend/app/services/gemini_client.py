"""Gemini API client with comprehensive error handling"""
from google import genai
from google.genai import types
import time
from typing import Tuple


class GeminiError(Exception):
    """Base exception for Gemini API errors"""
    pass


class QuotaExceededError(GeminiError):
    """Raised when API quota is exhausted"""
    pass


class GenerationTimeoutError(GeminiError):
    """Raised when generation takes too long"""
    pass


class GeminiClient:
    """Wrapper for Gemini API with error handling and timeout management"""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key
            timeout: Maximum generation time in seconds
        """
        self.client = genai.Client(api_key=api_key)
        self.timeout = timeout

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9"
    ) -> Tuple[bytes, int]:
        """
        Generate image from prompt

        Args:
            prompt: Text description of image to generate
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:3, 9:16)

        Returns:
            Tuple of (image_bytes, generation_time_ms)

        Raises:
            QuotaExceededError: API quota exhausted
            GenerationTimeoutError: Generation took too long
            GeminiError: Other generation failures
        """
        start = time.time()

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['Image']
                )
            )

            # Extract image
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    elapsed_ms = int((time.time() - start) * 1000)
                    return part.inline_data.data, elapsed_ms

            raise GeminiError("No image in response")

        except Exception as e:
            error_msg = str(e).lower()

            # Check for quota errors
            if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
                raise QuotaExceededError("API quota exceeded") from e

            # Check for timeout
            if time.time() - start > self.timeout:
                raise GenerationTimeoutError(f"Generation timeout after {self.timeout}s") from e

            # Generic error
            raise GeminiError(f"Generation failed: {e}") from e

