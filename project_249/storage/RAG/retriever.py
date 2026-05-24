from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from storage.database import Database


class Retriever:
    """
    RAG 检索器。
    
    负责从向量数据库中检索与查询最相关的文档。
    支持相似度阈值过滤和多种检索策略。
    """

    def __init__(
        self,
        database: "Database",
        k: int = 3,
        similarity_threshold: float = 0.0,
    ):
        """
        初始化检索器。
        
        参数：
            database: 向量数据库实例
            k: 每次检索返回的最大文档数量，默认为 3
            similarity_threshold: 相似度阈值，低于此阈值的文档将被过滤
                                  默认为 0.0（不过滤）
        """
        self.database = database
        self.k = k
        self.similarity_threshold = similarity_threshold

    def retrieve(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        检索与查询最相关的文档。
        
        参数：
            query: 查询文本
            k: 本次检索返回的最大文档数量，为 None 时使用初始化时的 k
            
        返回：
            与查询最相关的文档列表，按相似度从高到低排序
        """
        actual_k = k if k is not None else self.k

        results = self.database.query_with_scores(query, k=actual_k)

        if self.similarity_threshold > 0:
            results = [
                doc for doc, score in results
                if score >= self.similarity_threshold
            ]
        else:
            results = [doc for doc, score in results]

        return results

    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[Tuple[str, float]]:
        """
        检索与查询最相关的文档，并返回相似度分数。
        
        参数：
            query: 查询文本
            k: 本次检索返回的最大文档数量，为 None 时使用初始化时的 k
            
        返回：
            (文档文本, 相似度分数) 的元组列表，按相似度从高到低排序
        """
        actual_k = k if k is not None else self.k

        results = self.database.query_with_scores(query, k=actual_k)

        if self.similarity_threshold > 0:
            results = [
                (doc, score) for doc, score in results
                if score >= self.similarity_threshold
            ]

        return results

    def set_k(self, k: int):
        """
        设置默认的检索结果数量。
        
        参数：
            k: 新的检索结果数量
        """
        self.k = k

    def set_threshold(self, threshold: float):
        """
        设置相似度阈值。
        
        参数：
            threshold: 新的相似度阈值（0.0 到 1.0 之间）
        """
        self.similarity_threshold = max(0.0, min(1.0, threshold))

    def format_context(self, documents: List[str]) -> str:
        """
        将检索到的文档格式化为上下文文本。
        
        用于将检索结果拼接成适合 LLM 输入的格式。
        
        参数：
            documents: 文档列表
            
        返回：
            格式化后的上下文字符串
        """
        if not documents:
            return ""

        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[{i}] {doc}")

        return "\n\n".join(context_parts)


class HybridRetriever(Retriever):
    """
    混合检索器。
    
    结合向量相似度检索和关键词匹配的检索策略。
    可以提高特定场景下的检索准确性。
    """

    def __init__(
        self,
        database: "Database",
        k: int = 3,
        similarity_threshold: float = 0.0,
        keyword_weight: float = 0.3,
    ):
        """
        初始化混合检索器。
        
        参数：
            database: 向量数据库实例
            k: 每次检索返回的最大文档数量
            similarity_threshold: 相似度阈值
            keyword_weight: 关键词匹配在最终评分中的权重（0.0 到 1.0）
                            向量相似度权重为 1 - keyword_weight
        """
        super().__init__(database, k, similarity_threshold)
        self.keyword_weight = keyword_weight

    def _keyword_match_score(self, query: str, document: str) -> float:
        """
        计算查询与文档的关键词匹配分数。
        
        基于关键词出现的次数来计算匹配度。
        
        参数：
            query: 查询文本
            document: 文档文本
            
        返回：
            关键词匹配分数（0.0 到 1.0 之间）
        """
        query_words = set(query.lower().split())
        doc_words = document.lower().split()

        if not query_words:
            return 0.0

        match_count = sum(1 for word in query_words if word in doc_words)
        return match_count / len(query_words)

    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> List[Tuple[str, float]]:
        """
        使用混合策略检索文档。
        
        综合考虑向量相似度和关键词匹配度：
        最终分数 = 向量相似度 * (1 - keyword_weight) + 关键词分数 * keyword_weight
        
        参数：
            query: 查询文本
            k: 本次检索返回的最大文档数量
            
        返回：
            (文档文本, 混合分数) 的元组列表
        """
        actual_k = k if k is not None else self.k

        vector_results = self.database.query_with_scores(query, k=actual_k * 2)

        hybrid_results = []
        for doc, vector_score in vector_results:
            keyword_score = self._keyword_match_score(query, doc)
            hybrid_score = (
                vector_score * (1 - self.keyword_weight) +
                keyword_score * self.keyword_weight
            )
            hybrid_results.append((doc, hybrid_score))

        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        hybrid_results = hybrid_results[:actual_k]

        if self.similarity_threshold > 0:
            hybrid_results = [
                (doc, score) for doc, score in hybrid_results
                if score >= self.similarity_threshold
            ]

        return hybrid_results


def create_retriever(
    database: "Database",
    k: int = 3,
    similarity_threshold: float = 0.0,
    use_hybrid: bool = False,
    keyword_weight: float = 0.3,
) -> Retriever:
    """
    创建检索器实例的工厂函数。
    
    参数：
        database: 向量数据库实例
        k: 检索结果数量
        similarity_threshold: 相似度阈值
        use_hybrid: 是否使用混合检索（向量+关键词）
        keyword_weight: 混合检索中关键词的权重
        
    返回：
        检索器实例（Retriever 或 HybridRetriever）
    """
    if use_hybrid:
        return HybridRetriever(
            database=database,
            k=k,
            similarity_threshold=similarity_threshold,
            keyword_weight=keyword_weight,
        )
    else:
        return Retriever(
            database=database,
            k=k,
            similarity_threshold=similarity_threshold,
        )
