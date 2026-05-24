from typing import List, Dict, Any
from ..llms.deepseek_adapter import DeepSeekAdapter

Message = Dict[str, str]

llm = DeepSeekAdapter()


def _messages_to_text(messages: List[Message] | List[str]) -> str:
    texts = []
    for item in messages:
        if isinstance(item, dict):
            role = item.get("role", "")
            content = item.get("content", "")
            texts.append(f"{role}: {content}")
        else:
            texts.append(str(item))
    return "\n".join(texts)


def compare_history_messages(history_messages: List[Message] | List[str]) -> str:
    prompt = (
        "帮我把历史会话记录进行摘要总结，保留其中最关键的信息，"
        "只需要回复总结后的摘要，不要回复其他内容，历史会话记录如下：\n"
        + _messages_to_text(history_messages)
    )
    return llm.chat([{"role": "user", "content": prompt}])
