import os

from google import genai

from app.settings.environment_variables import load_environment


load_environment()


class EmbeddingService:
    def __init__(self) -> None:
        api_key = os.getenv("EMBEDDING_API_KEY")

        if not api_key:
            raise RuntimeError("EMBEDDING_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)

    def generate_embedding(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )

        return response.embeddings[0].values