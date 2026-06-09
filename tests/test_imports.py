"""
测试 Agent 模块导入和基本功能
"""

import pytest


class TestAgentImports:
    def test_simple_chat_agent_import(self):
        from project_249.agent.simple_chat import SimpleChatAgent
        assert SimpleChatAgent is not None

    def test_react_agent_import(self):
        from project_249.agent.react_agent import ReActAgent
        assert ReActAgent is not None

    def test_plan_execute_agent_import(self):
        from project_249.agent.plan_execute import PlanExecuteAgent
        assert PlanExecuteAgent is not None

    def test_agent_hub_import(self):
        from project_249.agent.hub import AgentHub
        assert AgentHub is not None

    def test_base_agent_import(self):
        from project_249.agent.base import BaseAgent
        assert BaseAgent is not None


class TestAgentVersion:
    def test_version_exists(self):
        from project_249 import __version__
        assert __version__ is not None
        assert len(__version__) > 0
        parts = __version__.split('.')
        assert len(parts) >= 2

    def test_version_matches_expected(self):
        from project_249 import __version__
        assert __version__ == "1.3.0", (
            f"版本号应该是 1.3.0，当前是 {__version__}。"
            "如果在进行版本发布，请更新此测试。"
        )


class TestMemoryImport:
    def test_short_term_memory_import(self):
        from project_249.memory.short_term import ShortTermMemory
        assert ShortTermMemory is not None

    def test_long_term_memory_import(self):
        from project_249.memory.long_term import LongTermMemory
        assert LongTermMemory is not None

    def test_strategy_enum_import(self):
        from project_249.memory.base import Strategy
        assert Strategy is not None
        assert hasattr(Strategy, 'SUMMARY')
        assert hasattr(Strategy, 'TRUNCATION')


class TestToolSystemImport:
    def test_parse_function_call_import(self):
        from project_249.tools.base import parse_function_call
        assert parse_function_call is not None

    def test_tools_import(self):
        from project_249.tools.tools_list import tools
        assert tools is not None
        assert isinstance(tools, list)
        assert len(tools) > 0
