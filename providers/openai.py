import os
from typing import AsyncIterator, List, Dict
from openai import AsyncOpenAI
from providers.base import BaseProvider

class OpenAIProvider(BaseProvider):
    """
    Provider for OpenAI models.
    """
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """
        Yields assistant tokens from OpenAI.
        """
        model = kwargs.get("model", "gpt-4-turbo")
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content 