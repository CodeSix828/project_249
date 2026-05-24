import pytest
from project_249.utils import Logger, LogLevel, LogCategory


class TestLogCategory:
    def test_category_values(self):
        assert LogCategory.AGENT.value == "agent"
        assert LogCategory.TOOL.value == "tool"
        assert LogCategory.MEMORY.value == "memory"
        assert LogCategory.LLM.value == "llm"
        assert LogCategory.WARN.value == "warn"
        assert LogCategory.ERROR.value == "error"

    def test_category_from_string(self):
        assert LogCategory("agent") == LogCategory.AGENT
        assert LogCategory("tool") == LogCategory.TOOL


class TestLogger:
    def test_default_enabled_categories(self):
        logger = Logger(verbose=False)
        enabled = logger.get_enabled_categories()
        
        assert LogCategory.AGENT in enabled
        assert LogCategory.TOOL in enabled
        assert LogCategory.ERROR in enabled
        assert LogCategory.MEMORY not in enabled
        assert LogCategory.LLM not in enabled

    def test_custom_enabled_categories(self):
        logger = Logger(
            verbose=False,
            enabled_categories=["agent", "llm"],
        )
        enabled = logger.get_enabled_categories()
        
        assert LogCategory.AGENT in enabled
        assert LogCategory.LLM in enabled
        assert LogCategory.TOOL not in enabled

    def test_enable_category(self):
        logger = Logger(verbose=False, enabled_categories=["agent"])
        logger.enable_category("tool")
        
        enabled = logger.get_enabled_categories()
        assert LogCategory.TOOL in enabled

    def test_disable_category(self):
        logger = Logger(verbose=False, enabled_categories=["agent", "tool"])
        logger.disable_category("agent")
        
        enabled = logger.get_enabled_categories()
        assert LogCategory.AGENT not in enabled
        assert LogCategory.TOOL in enabled

    def test_custom_handler(self):
        captured = []
        
        def custom_handler(level, message, category):
            captured.append({"level": level, "message": message, "category": category})
        
        logger = Logger(
            verbose=True,
            enabled_categories=["agent"],
            handler=custom_handler,
        )
        logger.agent("test message")
        
        assert len(captured) == 1
        assert captured[0]["message"] == "test message"
        assert captured[0]["category"] == LogCategory.AGENT

    def test_disabled_category_not_logged(self):
        captured = []
        
        def custom_handler(level, message, category):
            captured.append({"level": level, "message": message, "category": category})
        
        logger = Logger(
            verbose=True,
            enabled_categories=["agent"],
            handler=custom_handler,
        )
        logger.tool("should not be logged")
        logger.agent("should be logged")
        
        assert len(captured) == 1
        assert captured[0]["message"] == "should be logged"

    def test_verbose_false_no_output(self):
        captured = []
        
        def custom_handler(level, message, category):
            captured.append({"level": level, "message": message, "category": category})
        
        logger = Logger(
            verbose=False,
            handler=custom_handler,
        )
        logger.agent("test")
        
        assert len(captured) == 0

    def test_set_verbose(self):
        captured = []
        
        def custom_handler(level, message, category):
            captured.append({"level": level, "message": message, "category": category})
        
        logger = Logger(verbose=False, handler=custom_handler)
        logger.agent("no output")
        assert len(captured) == 0
        
        logger.set_verbose(True)
        logger.agent("output now")
        assert len(captured) == 1
