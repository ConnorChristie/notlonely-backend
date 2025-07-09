from typing import Protocol, AsyncIterator, List, Dict

class BaseProvider(Protocol):
    """
    Protocol for a provider that can generate text from a list of messages.
    """
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """
        Yields assistant tokens.
        """
        ...
        yield 