import asyncio
import os

from gemini_client import GeminiClient


async def main():
    client = GeminiClient(api_key=os.getenv("OPENAI_KEY"))
    text = await client.generate_async("how's the weather in Shanghai")
    print(text)
asyncio.run(main())