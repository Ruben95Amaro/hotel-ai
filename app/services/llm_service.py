import os
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from groq import Groq
from groq import APIError as GroqAPIError, APIConnectionError as GroqConnectionError, RateLimitError as GroqRateLimitError

from app.settings.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self._settings = get_settings()

        if self._settings.testing:
            self.client = None
            return

        api_key = os.getenv("LLM_API_KEY")

        if not api_key:
            raise RuntimeError("LLM_API_KEY is not configured.")

        self.client = Groq(api_key=api_key)
        self._model = self._settings.llm_model
        self._timeout = self._settings.llm_timeout_seconds
        self._max_retries = self._settings.llm_max_retries

    @property
    def _hotel_name(self) -> str:
        return self._settings.hotel_name
    
    @property
    def _hotel_location(self) -> str:
        return self._settings.hotel_location

    def _get_system_prompt(self) -> str:
        return (
            f"You are a hotel customer support assistant for {self._hotel_name} in {self._hotel_location}. "
            "Answer clearly and honestly. "
            "Only provide hotel-specific facts when they are "
            "supported by information provided in the conversation. "
            "If the information is missing, explicitly say that "
            "you do not have enough information to answer."
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((GroqAPIError, GroqConnectionError, GroqRateLimitError, asyncio.TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def generate_response(self, message: str) -> str:
        if self._settings.testing:
            # Return mock responses based on message content for testing
            message_lower = message.lower()
            if "check-in" in message_lower or "check in" in message_lower:
                return "Check-in starts at 15:00."
            if "check-out" in message_lower or "check out" in message_lower:
                return "Check-out is until 11:00."
            if "room" in message_lower:
                return "The hotel offers Standard Room, Deluxe Room, and Family Suite."
            if "facilit" in message_lower:
                return "The hotel provides outdoor swimming pool, fitness center, restaurant, bar, 24-hour reception, free Wi-Fi, and private parking."
            if "pet" in message_lower or "dog" in message_lower:
                return "Pets are allowed in selected rooms. Please contact the hotel to confirm availability."
            if "cancel" in message_lower:
                return "Reservations can be cancelled free of charge up to 48 hours before arrival."
            # Fallback for unrelated questions
            return "I don't have enough information to answer that question."

        loop = asyncio.get_event_loop()

        def _generate() -> str:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )
            return response.choices[0].message.content or ""

        return await asyncio.wait_for(
            loop.run_in_executor(None, _generate),
            timeout=self._timeout,
        )