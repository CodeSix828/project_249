"""
测试 LLM 模块：错误处理和异常类
"""

import pytest
from project_249.llms.deepseek_adapter import (
    LLMError,
    LLMTimeoutError,
    LLMAuthError,
    LLMRateLimitError,
)
from project_249.llms.deepseek_function_call import (
    ToolCallError,
    ToolCallTimeoutError,
    ToolCallAuthError,
    ToolCallRateLimitError,
)


class TestLLMExceptions:
    def test_llm_error_hierarchy(self):
        assert issubclass(LLMTimeoutError, LLMError)
        assert issubclass(LLMAuthError, LLMError)
        assert issubclass(LLMRateLimitError, LLMError)

    def test_llm_error_can_be_raised(self):
        with pytest.raises(LLMError):
            raise LLMError("test error")

        with pytest.raises(LLMError):
            raise LLMTimeoutError("timeout")

        err = LLMAuthError("auth failed")
        assert "auth failed" in str(err)

    def test_catch_specific_errors(self):
        try:
            raise LLMTimeoutError("request timed out")
        except LLMAuthError:
            assert False, "should not catch timeout as auth error"
        except LLMTimeoutError:
            pass

    def test_catch_base_error_catches_all(self):
        errors_caught = 0
        for err_cls in [LLMTimeoutError, LLMAuthError, LLMRateLimitError]:
            try:
                raise err_cls("test")
            except LLMError:
                errors_caught += 1
        assert errors_caught == 3


class TestToolCallExceptions:
    def test_tool_call_error_hierarchy(self):
        assert issubclass(ToolCallTimeoutError, ToolCallError)
        assert issubclass(ToolCallAuthError, ToolCallError)
        assert issubclass(ToolCallRateLimitError, ToolCallError)

    def test_tool_call_error_can_be_raised(self):
        with pytest.raises(ToolCallError):
            raise ToolCallTimeoutError("tool timeout")

    def test_tool_call_distinct_from_llm_error(self):
        assert not issubclass(ToolCallError, LLMError)
        assert not issubclass(LLMError, ToolCallError)


class TestDeepSeekAdapter:
    def test_adapter_initialization(self):
        from project_249.llms.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter()
        assert adapter is not None

    def test_adapter_has_chat_method(self):
        from project_249.llms.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter()
        assert hasattr(adapter, 'chat')
        assert hasattr(adapter, 'chat_stream')
        assert hasattr(adapter, 'chat_with_fallback')
        assert hasattr(adapter, 'validate_connection')

    def test_call_tool_initialization(self):
        from project_249.llms.deepseek_function_call import DeepSeekCallTool
        tool_caller = DeepSeekCallTool()
        assert tool_caller is not None
        assert hasattr(tool_caller, 'call_llm')
        assert hasattr(tool_caller, 'call_llm_with_fallback')
        assert hasattr(tool_caller, 'validate_connection')
