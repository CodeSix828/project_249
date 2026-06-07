import pytest
from project_249 import Strategy
from project_249.memory import ShortTermMemory


class TestShortTermMemory:
    def test_init_default_strategy(self):
        mem = ShortTermMemory(strategy=Strategy.SUMMARY)
        assert mem.strategy == Strategy.SUMMARY
        assert len(mem.historys) == 0

    def test_add_message(self):
        mem = ShortTermMemory(strategy=Strategy.SUMMARY)
        msg = {"role": "user", "content": "hello"}
        mem.add(msg)
        assert len(mem.historys) == 1
        assert mem.historys[0]["content"] == "hello"

    def test_sliding_window_keeps_recent(self):
        mem = ShortTermMemory(strategy=Strategy.SLIDING_WINDOW, window_size=3)
        for i in range(5):
            mem.add({"role": "user", "content": f"msg{i}"})
        assert len(mem.historys) == 5
        
        mem.retrieval()
        
        assert len(mem.historys) == 3
        assert mem.historys[0]["content"] == "msg2"
        assert mem.historys[1]["content"] == "msg3"
        assert mem.historys[2]["content"] == "msg4"

    def test_sliding_window_under_limit(self):
        mem = ShortTermMemory(strategy=Strategy.SLIDING_WINDOW, window_size=5)
        for i in range(3):
            mem.add({"role": "user", "content": f"msg{i}"})
        mem.retrieval()
        assert len(mem.historys) == 3

    def test_truncation_removes_oldest(self, monkeypatch):
        mem = ShortTermMemory(strategy=Strategy.TRUNCATION, max_token_num=50)
        mem.add({"role": "user", "content": "a" * 100})
        mem.add({"role": "user", "content": "b" * 100})
        mem.add({"role": "user", "content": "c"})
        
        original_len = len(mem.historys)
        mem.retrieval()
        
        assert len(mem.historys) <= original_len

    def test_summary_under_window_size(self):
        mem = ShortTermMemory(strategy=Strategy.SUMMARY, window_size=5)
        for i in range(3):
            mem.add({"role": "user", "content": f"msg{i}"})
        
        original_historys = list(mem.historys)
        mem.retrieval()
        
        assert len(mem.historys) == len(original_historys)


class TestStrategy:
    def test_strategy_values(self):
        assert Strategy.TRUNCATION.value == 0
        assert Strategy.SLIDING_WINDOW.value == 1
        assert Strategy.SUMMARY.value == 2
        assert Strategy.REFINE.value == 3
        assert Strategy.MAP_REDUCE.value == 4
        assert Strategy.MAP_RANK.value == 5
