import os
from typing import AsyncIterator, List, Dict
import ollama
from providers.base import BaseProvider

class OllamaProvider(BaseProvider):
    """
    Provider for Ollama models.
    """
    def __init__(self):
        self.client = ollama.AsyncClient(host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """
        Yields assistant tokens from Ollama.
        """
        model = kwargs.get("model", "llama3")
        stream = await self.client.chat(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            content = chunk['message']['content']
            if content:
                yield content 