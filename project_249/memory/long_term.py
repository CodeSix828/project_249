from typing import List, Optional
from .base import Strategy
from .base import compare_by_refine, compare_by_map_reduce, compare_by_map_rank
from ..utils.token_counter import calc_token_num
from ..storage.database import Database


class LongTermMemory:
    """
    长期记忆模块。
    
    长期记忆用于存储重要的对话历史和知识，
    可以在未来的对话中被检索和使用。
    
    特点：
    - 数据持久化存储在向量数据库中
    - 支持语义检索（基于相似度）
    - 支持对长文本进行摘要压缩
    - 与 RAG 系统共享向量存储能力
    """

    def __init__(
        self,
        strategy: Strategy = Strategy.MAP_REDUCE,
        store_path: str = "data/long_term_memory",
        single_max_token_num: int = 500,
    ):
        """
        初始化长期记忆。
        
        参数：
            strategy: 文本摘要策略，默认为 MAP_REDUCE
            store_path: 存储路径，默认为 data/long_term_memory
            single_max_token_num: 单条记忆的最大 token 数，超过此值会被摘要
        """
        self.historys: List[str] = []
        self.strategy = strategy
        self.single_max_token_num = single_max_token_num
        self.memory_retrieval = Database(store_path=store_path)

    def add(self, mem: str):
        """
        向长期记忆中添加一条记忆。
        
        参数：
            mem: 要存储的记忆文本
        """
        self.memory_retrieval.add(mem)

    def add_with_metadata(self, mem: str, metadata: Optional[dict] = None):
        """
        向长期记忆中添加一条记忆，并附带元数据。
        
        参数：
            mem: 要存储的记忆文本
            metadata: 元数据字典，可以包含时间、来源等信息
        """
        if metadata:
            metadata_str = f"[元数据: {metadata}] "
            mem = metadata_str + mem
        self.memory_retrieval.add(mem)

    def retrieval(self, query: str = "", k: int = 5) -> List[str]:
        """
        从长期记忆中检索与查询相关的记忆。
        
        流程：
        1. 从向量数据库检索最相关的 k 条记忆
        2. 对超过 token 限制的记忆进行摘要压缩
        3. 返回处理后的记忆列表
        
        参数：
            query: 查询文本，用于语义检索
            k: 返回的最大记忆数量，默认为 5
            
        返回：
            与查询相关的记忆列表
        """
        self.historys.clear()
        contexts = self.memory_retrieval.query(query, k=k)

        for content in contexts:
            token_num = calc_token_num(content)
            if token_num <= self.single_max_token_num:
                self.historys.append(content)
                continue

            if self.strategy == Strategy.REFINE:
                summary = compare_by_refine(content)
            elif self.strategy == Strategy.MAP_REDUCE:
                summary = compare_by_map_reduce(content)
            elif self.strategy == Strategy.MAP_RANK:
                summary = compare_by_map_rank(content)
            else:
                summary = compare_by_map_reduce(content)

            self.historys.append(summary)

        return self.historys

    def retrieval_with_scores(
        self,
        query: str = "",
        k: int = 5,
    ) -> List[tuple]:
        """
        从长期记忆中检索与查询相关的记忆，并返回相似度分数。
        
        参数：
            query: 查询文本
            k: 返回的最大记忆数量
            
        返回：
            (记忆文本, 相似度分数) 的元组列表
        """
        return self.memory_retrieval.query_with_scores(query, k=k)

    def count(self) -> int:
        """
        返回长期记忆中的记忆总数。
        
        返回：
            记忆总数
        """
        return self.memory_retrieval.count()

    def clear(self):
        """
        清空所有长期记忆（包括磁盘存储）。
        
        警告：此操作不可恢复！
        """
        self.memory_retrieval.clear()
        self.historys.clear()

    def set_strategy(self, strategy: Strategy):
        """
        设置摘要策略。
        
        参数：
            strategy: 新的摘要策略（REFINE、MAP_REDUCE 或 MAP_RANK）
        """
        self.strategy = strategy

    def format_for_context(self) -> str:
        """
        将当前检索到的记忆格式化为上下文文本。
        
        用于将记忆整理成适合 LLM 输入的格式。
        
        返回：
            格式化的上下文字符串
        """
        if not self.historys:
            return ""

        parts = ["【长期记忆】"]
        for i, mem in enumerate(self.historys, 1):
            parts.append(f"{i}. {mem}")

        return "\n".join(parts)
