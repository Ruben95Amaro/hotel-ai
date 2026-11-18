import hashlib
import os
import asyncio
import re
from collections import Counter
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from google import genai
from google.genai import errors as genai_errors

from app.settings.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self._settings = get_settings()

        if self._settings.testing:
            self.client = None
            # Build vocabulary from hotel document for better mock embeddings
            self._vocab = self._build_vocab()
            return

        api_key = os.getenv("EMBEDDING_API_KEY")

        if not api_key:
            raise RuntimeError("EMBEDDING_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)
        self._model = self._settings.embedding_model
        self._timeout = self._settings.embedding_timeout_seconds
        self._max_retries = self._settings.embedding_max_retries

    def _build_vocab(self) -> dict[str, int]:
        """Build vocabulary from hotel document for mock embeddings."""
        vocab = {}
        # Key hotel-related terms that should have semantic similarity
        hotel_terms = [
            # Check-in/out and opening hours
            "check", "in", "out", "check-in", "check-out", "checkin", "checkout",
            "open", "opening", "hours", "reception", "24-hour", "24/7", "available",
            "arrival", "departure", "time", "when", "start", "end", "close",
            # Rooms
            "room", "rooms", "standard", "deluxe", "family", "suite", "bedroom",
            "occupancy", "guest", "guests", "bed", "beds", "single", "double", "king",
            "sofa", "bathroom", "private", "view", "sea",
            # Hotel info
            "hotel", "grand", "ocean", "lisbon", "portugal", "address", "phone",
            "location", "located", "where", "contact", "email",
            # Facilities
            "facilities", "pool", "fitness", "restaurant", "bar", "reception",
            "wifi", "wi-fi", "parking", "parking", "service", "services",
            "amenities", "included", "breakfast", "additional", "fee",
            # Pets
            "pets", "pet", "dog", "cat", "allowed", "availability", "confirm",
            # Cancellation
            "cancellation", "cancel", "policy", "charge", "hours", "arrival",
            "refund", "free", "penalty", "fee",
            # Pricing
            "price", "rate", "cost", "euro", "eur", "night", "per",
            # Booking
            "booking", "reserve", "reservation", "reservation",
            # General
            "nearby", "attractions", "transport", "metro", "airport",
        ]
        for i, term in enumerate(hotel_terms):
            vocab[term.lower()] = i
        return vocab

    def _text_to_vector(self, text: str) -> list[float]:
        """Convert text to a semantic mock embedding vector."""
        # Simple TF-IDF-like approach using vocabulary
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        
        # Create vector based on vocabulary matches
        vocab_size = max(len(self._vocab), 100)
        vector = [0.0] * 768
        
        for word, count in word_counts.items():
            if word in self._vocab:
                idx = self._vocab[word] % 768
                # Weight by count
                vector[idx] += count * 1.0
        
        # Add some hash-based noise for uniqueness but keep semantic signal
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        for i in range(768):
            byte_index = i % len(hash_bytes)
            # Blend semantic signal (70%) with hash noise (30%)
            vector[i] = 0.7 * vector[i] + 0.3 * ((hash_bytes[byte_index] / 255.0) * 2 - 1)
        
        # Normalize
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((genai_errors.APIError, asyncio.TimeoutError, ConnectionError)),
        reraise=True,
    )
    async def generate_embedding(self, text: str) -> list[float]:
        if self._settings.testing:
            return self._text_to_vector(text)

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
            return self._text_to_vector(text)

        response = self.client.models.embed_content(
            model=self._model,
            contents=text,
        )
        return response.embeddings[0].values