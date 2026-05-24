import pytest
from project_249 import SimpleChatAgent, Strategy


class TestSimpleChatAgent:
    def test_init_with_short_term_memory(self):
        agent = SimpleChatAgent(
            memory_type="short_term",
            verbose=False,
        )
        assert agent.verbose is False
        assert agent.memory is not None

    def test_init_with_custom_logs(self):
        agent = SimpleChatAgent(
            memory_type="short_term",
            verbose=False,
            enabled_logs=["agent", "error"],
        )
        enabled = agent.get_enabled_logs()
        assert "agent" in enabled
        assert "error" in enabled
        assert "tool" not in enabled

    def test_set_verbose(self):
        agent = SimpleChatAgent("short_term", verbose=False)
        assert agent.verbose is False
        
        agent.set_verbose(True)
        assert agent.verbose is True

    def test_set_enabled_logs(self):
        agent = SimpleChatAgent("short_term", verbose=False)
        agent.set_enabled_logs(["llm"])
        
        enabled = agent.get_enabled_logs()
        assert "llm" in enabled
        assert "agent" not in enabled

    def test_enable_disable_log(self):
        agent = SimpleChatAgent("short_term", verbose=False)
        agent.set_enabled_logs(["agent"])
        
        agent.enable_log("memory")
        assert "memory" in agent.get_enabled_logs()
        
        agent.disable_log("agent")
        assert "agent" not in agent.get_enabled_logs()

    def test_init_with_summary_strategy(self):
        agent = SimpleChatAgent(
            memory_type="short_term",
            compare_type=Strategy.SUMMARY,
            verbose=False,
        )
        assert agent.memory.strategy == Strategy.SUMMARY

    def test_init_with_sliding_window_strategy(self):
        agent = SimpleChatAgent(
            memory_type="short_term",
            compare_type=Strategy.SLIDING_WINDOW,
            verbose=False,
        )
        assert agent.memory.strategy == Strategy.SLIDING_WINDOW
