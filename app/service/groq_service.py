from app.config.settings import GROQ_KEY
from groq import Groq
from app.prompt.System_prompt import SYSTEM_PROMPT

client = Groq(api_key=GROQ_KEY)
class GroqService:
    @staticmethod
    def stream(history: list):
        try:
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ] + history

            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.7,
                stream=True
            )


            for chunk in stream:
                content = chunk.choices[0].delta.content

                if content:
                    yield content

        except Exception as e:
            return f"Some error occurred: {str(e)}"