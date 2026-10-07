
import os

from groq import Groq

from app.settings.environment_variables import load_environment

load_environment()

class LLMService:
    def __init__(self) -> None:
        environment = os.getenv("ENVIRONMENT")
        api_key = os.getenv("LLM_API_KEY", environment)


        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self.client = Groq(
            api_key=api_key,
            timeout=30000,
        )

    def generate_response(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for a hotel. "
                        "Answer clearly and honestly. "
                        "If you do not know a hotel-specific fact, "
                        "say that you do not have that information."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
        )

        return response.choices[0].message.content or ""
