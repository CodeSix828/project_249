from abc import ABC, abstractmethod
from typing import Iterator, List, Dict, Any, Optional


Message = Dict[str, str]


class BaseLLM(ABC):
    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        pass

    def chat_stream(
        self,
        messages: List[Message],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Iterator[str]:
        response = self.chat(messages, max_tokens, temperature, **kwargs)
        for char in response:
            yield char
