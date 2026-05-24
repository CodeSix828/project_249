from enum import Enum
from typing import Callable, Optional, Set, List
from datetime import datetime


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class LogCategory(Enum):
    AGENT = "agent"
    TOOL = "tool"
    MEMORY = "memory"
    LLM = "llm"
    WARN = "warn"
    ERROR = "error"


DEFAULT_ENABLED_CATEGORIES = {
        LogCategory.AGENT, LogCategory.TOOL, LogCategory.ERROR}


LogHandler = Callable[[LogLevel, str, Optional[LogCategory]], None]


def _default_console_handler(
    level: LogLevel,
    message: str,
    category: Optional[LogCategory] = None,
):
    timestamp = datetime.now().strftime("%H:%M:%S")
    level_prefix = {
        LogLevel.DEBUG: "[DEBUG]",
        LogLevel.INFO: "[INFO]",
        LogLevel.WARN: "[WARN]",
        LogLevel.ERROR: "[ERROR]",
    }
    category_prefix = ""
    if category:
        category_map = {
            LogCategory.AGENT: "[Agent]",
            LogCategory.TOOL: "[Tool]",
            LogCategory.MEMORY: "[Memory]",
            LogCategory.LLM: "[LLM]",
            LogCategory.WARN: "[Warn]",
            LogCategory.ERROR: "[Error]",
        }
        category_prefix = f" {category_map[category]}"
    print(f"{timestamp} {level_prefix[level]}{category_prefix} {message}")


class Logger:
    def __init__(
        self,
        verbose: bool = True,
        min_level: LogLevel = LogLevel.INFO,
        enabled_categories: Optional[Set[LogCategory] | List[str] | None] = None,
        handler: Optional[LogHandler] = None,
    ):
        self.verbose = verbose
        self.min_level = min_level
        self._handler = handler or _default_console_handler
        self._enabled_categories = self._normalize_categories(enabled_categories)

    @staticmethod
    def _normalize_categories(
        categories: Optional[Set[LogCategory] | List[str] | None]) -> Set[LogCategory]:
        if categories is None:
            return DEFAULT_ENABLED_CATEGORIES.copy()
        result: Set[LogCategory] = set()
        for c in categories:
            if isinstance(c, LogCategory):
                result.add(c)
            elif isinstance(c, str):
                try:
                    result.add(LogCategory(c.lower()))
                except ValueError:
                    pass
        return result if result else DEFAULT_ENABLED_CATEGORIES.copy()

    def _log(
        self,
        level: LogLevel,
        message: str,
        category: Optional[LogCategory] = None,
    ):
        if not self.verbose:
            return
        if level.value < self.min_level.value:
            return
        if category is not None and category not in self._enabled_categories:
            return
        self._handler(level, message, category)

    def agent(self, message: str):
        self._log(LogLevel.INFO, message, LogCategory.AGENT)

    def tool(self, message: str):
        self._log(LogLevel.INFO, message, LogCategory.TOOL)

    def memory(self, message: str):
        self._log(LogLevel.DEBUG, message, LogCategory.MEMORY)

    def llm(self, message: str):
        self._log(LogLevel.DEBUG, message, LogCategory.LLM)

    def warn(self, message: str):
        self._log(LogLevel.WARN, message, LogCategory.WARN)

    def error(self, message: str):
        self._log(LogLevel.ERROR, message, LogCategory.ERROR)

    def debug(self, message: str, category: Optional[LogCategory] = None):
        self._log(LogLevel.DEBUG, message, category)

    def info(self, message: str, category: Optional[LogCategory] = None):
        self._log(LogLevel.INFO, message, category)

    def set_handler(self, handler: LogHandler):
        self._handler = handler

    def set_verbose(self, verbose: bool):
        self.verbose = verbose

    def set_min_level(self, level: LogLevel):
        self.min_level = level

    def set_enabled_categories(
        self,
        categories: Set[LogCategory] | List[str] | None):
        self._enabled_categories = self._normalize_categories(categories)

    def enable_category(self, category: LogCategory | str):
        if isinstance(category, str):
            category = LogCategory(category.lower())
        self._enabled_categories.add(category)

    def disable_category(self, category: LogCategory | str):
        if isinstance(category, str):
            category = LogCategory(category.lower())
        if category in self._enabled_categories:
            self._enabled_categories.discard(category)

    def get_enabled_categories(self) -> Set[LogCategory]:
        return self._enabled_categories.copy()


_default_logger: Optional[Logger] = None


def get_logger() -> Logger:
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger()
    return _default_logger
