from typing import List, Dict, Any
from .base import Strategy
from .summarizer import compare_history_messages, _messages_to_text
from ..utils.token_counter import calc_token_num

Message = Dict[str, str]


class ShortTermMemory:
    def __init__(
        self,
        strategy=Strategy.SUMMARY,
        window_size=5,
        max_token_num=2000,
    ):
        self.historys: List[Message] = []
        self.strategy = strategy
        self.window_size = window_size
        self.max_token_num = max_token_num

    def add(self, mem: Message):
        self.historys.append(mem)

    def retrieval(self, query: str = ""):
        if self.strategy == Strategy.TRUNCATION:
            self._apply_truncation()
        elif self.strategy == Strategy.SLIDING_WINDOW:
            self._apply_sliding_window()
        elif self.strategy == Strategy.SUMMARY:
            self._apply_summary()

    def _apply_truncation(self):
        while self.historys:
            history_text = _messages_to_text(self.historys)
            token_num = calc_token_num(history_text)
            if token_num <= self.max_token_num:
                break
            self.historys.pop(0)

    def _apply_sliding_window(self):
        if len(self.historys) > self.window_size:
            self.historys = self.historys[-self.window_size:]

    def _apply_summary(self):
        if len(self.historys) <= self.window_size:
            return
        
        keep_count = self.window_size - 1
        if keep_count < 1:
            keep_count = 1
        
        summarize_count = len(self.historys) - keep_count
        if summarize_count <= 0:
            return
        
        to_summarize = self.historys[:summarize_count]
        to_keep = self.historys[summarize_count:]
        
        try:
            summary_text = compare_history_messages(to_summarize)
            summary_message = {"role": "assistant", "content": f"[历史摘要] {summary_text}"}
            self.historys = [summary_message] + to_keep
        except Exception:
            self.historys = to_keep
