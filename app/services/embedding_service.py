import os
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from google import genai
from google.genai import errors as genai_errors

from app.settings.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self._settings = get_settings()

        if self._settings.testing:
            # Use mock client for testing
            self.client = None
            return

        api_key = os.getenv("EMBEDDING_API_KEY")

        if not api_key:
            raise RuntimeError("EMBEDDING_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)
        self._model = self._settings.embedding_model
        self._timeout = self._settings.embedding_timeout_seconds
        self._max_retries = self._settings.embedding_max_retries

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((genai_errors.APIError, asyncio.TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def generate_embedding(self, text: str) -> list[float]:
        if self._settings.testing:
            # Return a deterministic mock embedding for testing
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            # Convert to a list of 768 floats (typical embedding size)
            return [(b / 255.0) for b in hash_obj.digest()] * 48  # 16 * 48 = 768

        loop = asyncio.get_event_loop()

        def _embed() -> list[float]:
            response = self.client.models.embed_content(
                model=self._model,
                contents=text,
            )
            return response.embeddings[0].values

        return await asyncio.wait_for(
            loop.run_in_executor(None, _embed),
            timeout=self._timeout,
        )

    def generate_embedding_sync(self, text: str) -> list[float]:
        """Synchronous version for startup ingestion."""
        if self._settings.testing:
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            return [(b / 255.0) for b in hash_obj.digest()] * 48

        response = self.client.models.embed_content(
            model=self._model,
            contents=text,
        )
        return response.embeddings[0].values