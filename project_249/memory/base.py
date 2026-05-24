from enum import Enum


class Strategy(Enum):
    DEFAULT = -1
    TRUNCATTON = 0
    SLIDING_WINDOW = 1
    SUMMARY = 2
    REFINE = 3
    MAP_REDUCE = 4
    MAP_RANK = 5


import re
from .summarizer import compare_history_messages


def _split_content(content: str) -> list[str]:
    sentences = re.split(r"[。！？!?\n]+", content)
    return [s.strip() for s in sentences if s.strip()]


def compare_by_refine(content: str) -> str:
    sentences = _split_content(content)
    if not sentences:
        return ""
    
    summary = sentences[0]
    for sentence in sentences[1:]:
        summary = compare_history_messages([summary, sentence])
    return summary


def compare_by_map_reduce(content: str) -> str:
    sentences = _split_content(content)
    if not sentences:
        return ""
    
    summaries = []
    for sentence in sentences:
        summary = compare_history_messages([sentence])
        summaries.append(summary)
    
    final_summary = compare_history_messages(summaries)
    return final_summary


def summary_and_grade(chunk: str) -> dict | None:
    from llms.deepseek_adapter import DeepSeekAdapter
    
    llm = DeepSeekAdapter()
    prompt = f"""请对以下文本进行摘要总结，并给摘要的质量打分（0-1分）。
只输出JSON格式，格式如下：
{{"summary": "摘要内容", "grade": 0.85}}

文本：
{chunk}"""
    
    try:
        response = llm.chat([{"role": "user", "content": prompt}])
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            import json
            obj = json.loads(match.group(0))
            obj["grade"] = float(obj.get("grade", 0))
            return obj
    except Exception:
        pass
    return None


def compare_by_map_rank(content: str) -> str:
    sentences = _split_content(content)
    if not sentences:
        return ""
    
    sum_objs = []
    for sentence in sentences:
        sum_obj = summary_and_grade(sentence)
        if sum_obj:
            sum_objs.append(sum_obj)
    
    if not sum_objs:
        return sentences[0]
    
    sum_objs.sort(key=lambda item: item.get("grade", 0), reverse=True)
    return sum_objs[0].get("summary", sentences[0])
