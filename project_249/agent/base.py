from abc import ABC, abstractmethod
from typing import Iterator, Optional, List
from ..utils.logger import LogHandler


class BaseAgent(ABC):
    @abstractmethod
    def chat(self, user_input: str) -> str:
        pass

    def chat_stream(self, user_input: str) -> Iterator[str]:
        response = self.chat(user_input)
        for char in response:
            yield char

    def set_verbose(self, verbose: bool) -> None:
        pass

    def set_log_handler(self, handler: LogHandler) -> None:
        pass

    def set_enabled_logs(self, categories: List[str] | None) -> None:
        pass

    def get_enabled_logs(self) -> List[str]:
        return []
