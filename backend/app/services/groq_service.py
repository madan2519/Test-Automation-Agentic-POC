from groq import Groq
from config.settings import settings
from utils.logger import logger

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    async def generate_response(self, prompt: str, system_prompt: str = "You are a helpful AI assistant."):
        try:
            import asyncio
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise e
        
class OpenaiService:
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"

    async def generate_response(self, prompt: str, system_prompt: str = "You are a helpful AI assistant."):
        try:
            import asyncio
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise e

groq_service = GroqService()
openai_service = OpenaiService()
