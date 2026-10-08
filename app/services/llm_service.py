import os

from groq import Groq

from app.settings.environment_variables import load_environment


load_environment()


class LLMService:
    def __init__(self) -> None:
        api_key = os.getenv("LLM_API_KEY")

        if not api_key:
            raise RuntimeError("LLM_API_KEY is not configured.")

        self.client = Groq(api_key=api_key)

    def generate_response(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return response.choices[0].message.content or ""