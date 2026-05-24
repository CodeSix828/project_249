from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..storage.database import Database
    from ..llms.base import BaseLLM

from ..storage.RAG.retriever import Retriever, create_retriever
from ..llms.deepseek_adapter import DeepSeekAdapter


RAG_SYSTEM_PROMPT = """你是一个基于检索增强生成（RAG）的AI助手。

## 核心能力
- 你可以访问一个知识库来回答用户的问题
- 你需要基于检索到的上下文信息来回答问题
- 如果检索到的信息不足以回答问题，如实告知用户

## 回答规则
1. **基于上下文**：尽量使用检索到的上下文信息来回答问题
2. **引用来源**：如果引用了上下文中的信息，可以在回答中明确指出（如"根据资料显示..."）
3. **不要编造**：如果上下文中没有相关信息，不要编造答案
4. **信息不足**：如果检索到的信息不足以回答问题，告诉用户"根据现有资料，我无法确定这个问题的答案"或类似表述
5. **综合信息**：如果检索到多个相关信息，综合整理后给出回答

## 回答格式
- 直接给出答案，不要重复问题
- 如果上下文不相关，礼貌地说明无法回答
- 回答要简洁、准确、有用"""


class RAGChain:
    """
    RAG 链（检索增强生成链）。
    
    RAG 链是 RAG 系统的核心组件，负责：
    1. 接收用户查询
    2. 从向量数据库检索相关文档
    3. 将检索到的文档作为上下文提供给 LLM
    4. 基于上下文生成回答
    
    这是一个典型的"检索-生成"流程。
    """

    def __init__(
        self,
        retriever: Retriever,
        llm: Optional["BaseLLM"] = None,
        system_prompt: str = RAG_SYSTEM_PROMPT,
    ):
        """
        初始化 RAG 链。
        
        参数：
            retriever: 检索器实例，用于检索相关文档
            llm: 语言模型实例，为 None 时使用默认的 DeepSeekAdapter
            system_prompt: 系统提示词，用于指导 LLM 如何回答
        """
        self.retriever = retriever
        self.llm = llm if llm is not None else DeepSeekAdapter()
        self.system_prompt = system_prompt

    def _build_messages(
        self,
        query: str,
        context: str,
    ) -> List[Dict[str, str]]:
        """
        构建发送给 LLM 的消息列表。
        
        参数：
            query: 用户查询
            context: 检索到的上下文字符串
            
        返回：
            符合 OpenAI 格式的消息列表
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        if context:
            messages.append({
                "role": "user",
                "content": f"以下是检索到的相关信息：\n\n{context}\n\n请基于以上信息回答问题。"
            })

        messages.append({
            "role": "user",
            "content": query
        })

        return messages

    def invoke(self, query: str) -> str:
        """
        执行 RAG 链，生成回答。
        
        流程：
        1. 使用检索器从知识库检索相关文档
        2. 将检索到的文档格式化为上下文
        3. 构建消息并调用 LLM
        4. 返回生成的回答
        
        参数：
            query: 用户查询
            
        返回：
            基于检索到的上下文生成的回答
        """
        documents = self.retriever.retrieve(query)
        context = self.retriever.format_context(documents)

        messages = self._build_messages(query, context)

        return self.llm.chat(messages)

    def invoke_stream(self, query: str) -> Iterator[str]:
        """
        执行 RAG 链，以流式方式生成回答。
        
        与 invoke() 类似，但返回一个迭代器，可以逐字获取回答。
        适合需要实时显示输出的场景。
        
        参数：
            query: 用户查询
            
        返回：
            文本块的迭代器
        """
        documents = self.retriever.retrieve(query)
        context = self.retriever.format_context(documents)

        messages = self._build_messages(query, context)

        yield from self.llm.chat_stream(messages)

    def invoke_with_context(self, query: str) -> Dict[str, Any]:
        """
        执行 RAG 链，返回回答和检索到的上下文。
        
        此方法可以让你获取到 LLM 使用了哪些上下文信息，
        便于调试和展示来源。
        
        参数：
            query: 用户查询
            
        返回：
            包含 'answer' 和 'contexts' 的字典：
            - answer: LLM 生成的回答
            - contexts: 检索到的文档列表（包含分数）
        """
        documents_with_scores = self.retriever.retrieve_with_scores(query)
        documents = [doc for doc, _ in documents_with_scores]
        context = self.retriever.format_context(documents)

        messages = self._build_messages(query, context)
        answer = self.llm.chat(messages)

        return {
            "answer": answer,
            "contexts": documents_with_scores,
        }

    def set_retriever_k(self, k: int):
        """
        设置检索器返回的文档数量。
        
        参数：
            k: 新的文档数量
        """
        self.retriever.set_k(k)

    def set_threshold(self, threshold: float):
        """
        设置相似度阈值。
        
        参数：
            threshold: 新的相似度阈值（0.0 到 1.0 之间）
        """
        self.retriever.set_threshold(threshold)


def create_rag_chain(
    database: "Database",
    k: int = 3,
    similarity_threshold: float = 0.0,
    use_hybrid: bool = False,
    keyword_weight: float = 0.3,
    llm: Optional["BaseLLM"] = None,
) -> RAGChain:
    """
    创建 RAG 链实例的工厂函数。
    
    参数：
        database: 向量数据库实例
        k: 检索结果数量
        similarity_threshold: 相似度阈值
        use_hybrid: 是否使用混合检索（向量+关键词）
        keyword_weight: 混合检索中关键词的权重
        llm: 语言模型实例，为 None 时使用默认的 DeepSeekAdapter
        
    返回：
        RAGChain 实例
    """
    retriever = create_retriever(
        database=database,
        k=k,
        similarity_threshold=similarity_threshold,
        use_hybrid=use_hybrid,
        keyword_weight=keyword_weight,
    )

    return RAGChain(retriever=retriever, llm=llm)


def simple_rag_query(
    database: "Database",
    query: str,
    k: int = 3,
) -> str:
    """
    简化版 RAG 查询函数。
    
    适合快速使用，不需要复杂配置的场景。
    
    参数：
        database: 向量数据库实例
        query: 用户查询
        k: 检索结果数量
        
    返回：
        生成的回答
    """
    chain = create_rag_chain(database=database, k=k)
    return chain.invoke(query)
