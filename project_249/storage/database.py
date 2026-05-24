import json
import os
from typing import List, Optional
import numpy as np
from .RAG.embeddings import EmbeddingService


class Database:
    """
    向量数据库类，用于存储和检索文档及其向量表示。
    
    功能：
    - 存储文档文本及其对应的嵌入向量
    - 根据查询文本检索最相关的文档
    - 支持持久化到磁盘（JSON格式）
    """

    def __init__(self, store_path: str = "."):
        """
        初始化向量数据库。
        
        参数：
            store_path: 数据库文件存储的目录路径，默认为当前目录
        """
        if not os.path.exists(store_path):
            os.makedirs(store_path)
        
        self.vector_path = os.path.join(store_path, "vector.json")
        self.doc_path = os.path.join(store_path, "document.json")
        self.vectors: List[List[float]] = []
        self.documents: List[str] = []
        self.embedding_service = EmbeddingService()
        
        self.load()

    def dump(self, vectors: List[List[float]], documents: List[str]):
        """
        将向量列表和文档列表保存到磁盘。
        
        参数：
            vectors: 嵌入向量列表
            documents: 文档文本列表
        """
        with open(self.vector_path, 'w', encoding='utf-8') as f:
            json.dump(vectors, f, ensure_ascii=False, indent=2)
        
        with open(self.doc_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)

    def load(self):
        """
        从磁盘加载向量和文档数据到内存。
        如果文件不存在，则保持空列表。
        """
        if os.path.exists(self.vector_path) and os.path.exists(self.doc_path):
            with open(self.vector_path, 'r', encoding='utf-8') as f:
                self.vectors = json.load(f)
            
            with open(self.doc_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)

    def add(self, chunk: str):
        """
        向数据库中添加单个文档块。
        
        流程：
        1. 将文本块转换为嵌入向量
        2. 将向量和文本添加到内存列表
        3. 保存到磁盘
        
        参数：
            chunk: 要添加的文档文本块
        """
        vector = self.embedding_service.get_vector(chunk)
        self.vectors.append(vector)
        self.documents.append(chunk)
        self.dump(self.vectors, self.documents)

    def add_documents(self, chunks: List[str]):
        """
        批量添加多个文档块。
        
        相比多次调用 add()，此方法更高效，因为只保存一次到磁盘。
        
        参数：
            chunks: 文档文本块列表
        """
        for chunk in chunks:
            vector = self.embedding_service.get_vector(chunk)
            self.vectors.append(vector)
            self.documents.append(chunk)
        
        self.dump(self.vectors, self.documents)

    def search(self, query_vector: List[float], k: int = 3) -> List[str]:
        """
        根据查询向量搜索最相关的 k 个文档。
        
        使用余弦相似度计算相似度。
        
        参数：
            query_vector: 查询文本的嵌入向量
            k: 返回的最相关文档数量，默认为 3
            
        返回：
            按相似度从高到低排序的文档列表
        """
        if not self.vectors:
            return []
        
        similarities = np.array([
            self.embedding_service.get_similarity(query_vector, vector)
            for vector in self.vectors
        ])
        
        top_indices = similarities.argsort()[-k:][::-1]
        return [self.documents[i] for i in top_indices]

    def search_with_scores(self, query_vector: List[float], k: int = 3) -> List[tuple]:
        """
        根据查询向量搜索最相关的 k 个文档，并返回相似度分数。
        
        参数：
            query_vector: 查询文本的嵌入向量
            k: 返回的最相关文档数量，默认为 3
            
        返回：
            (文档文本, 相似度分数) 的元组列表，按相似度从高到低排序
        """
        if not self.vectors:
            return []
        
        similarities = np.array([
            self.embedding_service.get_similarity(query_vector, vector)
            for vector in self.vectors
        ])
        
        top_indices = similarities.argsort()[-k:][::-1]
        return [(self.documents[i], float(similarities[i])) for i in top_indices]

    def query(self, query: str, k: int = 3) -> List[str]:
        """
        根据查询文本搜索最相关的 k 个文档。
        
        这是 search() 的便捷方法，会自动将查询文本转换为向量。
        
        参数：
            query: 查询文本
            k: 返回的最相关文档数量，默认为 3
            
        返回：
            按相似度从高到低排序的文档列表
        """
        query_vector = self.embedding_service.get_vector(query)
        return self.search(query_vector, k)

    def query_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """
        根据查询文本搜索最相关的 k 个文档，并返回相似度分数。
        
        参数：
            query: 查询文本
            k: 返回的最相关文档数量，默认为 3
            
        返回：
            (文档文本, 相似度分数) 的元组列表
        """
        query_vector = self.embedding_service.get_vector(query)
        return self.search_with_scores(query_vector, k)

    def clear(self):
        """
        清空数据库（内存和磁盘）。
        """
        self.vectors = []
        self.documents = []
        
        if os.path.exists(self.vector_path):
            os.remove(self.vector_path)
        
        if os.path.exists(self.doc_path):
            os.remove(self.doc_path)

    def count(self) -> int:
        """
        返回数据库中的文档数量。
        
        返回：
            文档总数
        """
        return len(self.documents)


