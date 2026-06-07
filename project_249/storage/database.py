import os
import json
from typing import List, Optional
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .RAG.embeddings import EmbeddingService


class Database:
    """
    向量数据库类，用于存储和检索文档及其向量表示。
    
    功能：
    - 存储文档文本及其对应的嵌入向量
    - 根据查询文本检索最相关的文档
    - 支持两种后端：ChromaDB（推荐）或 JSON文件（兼容旧版）
    """

    def __init__(
        self,
        store_path: str = ".",
        backend: str = "chroma",
        collection_name: str = "project_249_collection",
    ):
        """
        初始化向量数据库。
        
        参数：
            store_path: 数据库文件存储的目录路径，默认为当前目录
            backend: 使用的后端类型，"chroma"（默认）或 "json"
            collection_name: ChromaDB 集合名称，仅在 backend="chroma" 时使用
        """
        if not os.path.exists(store_path):
            os.makedirs(store_path)
        
        self.store_path = store_path
        self.backend = backend.lower()
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            self._init_chroma(collection_name)
        else:
            self._init_json()

    def _init_chroma(self, collection_name: str):
        """初始化 ChromaDB 后端"""
        self._chroma_client = chromadb.PersistentClient(
            path=self.store_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # 尝试获取已有集合，或创建新集合
        try:
            self._collection = self._chroma_client.get_collection(
                name=collection_name,
                embedding_function=None  # 我们使用自己的 embedding
            )
        except Exception:
            self._collection = self._chroma_client.create_collection(
                name=collection_name,
                embedding_function=None,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
        
        self._ids: List[str] = []

    def _init_json(self):
        """初始化 JSON 文件后端（兼容旧版）"""
        self.vector_path = os.path.join(self.store_path, "vector.json")
        self.doc_path = os.path.join(self.store_path, "document.json")
        self.vectors: List[List[float]] = []
        self.documents: List[str] = []
        self.load()

    def dump(self, vectors: List[List[float]], documents: List[str]):
        """
        将向量列表和文档列表保存到磁盘（JSON后端使用）。
        
        参数：
            vectors: 嵌入向量列表
            documents: 文档文本列表
        """
        if self.backend != "json":
            return
            
        with open(self.vector_path, 'w', encoding='utf-8') as f:
            json.dump(vectors, f, ensure_ascii=False, indent=2)
        
        with open(self.doc_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)

    def load(self):
        """
        从磁盘加载向量和文档数据到内存（JSON后端使用）。
        如果文件不存在，则保持空列表。
        """
        if self.backend != "json":
            return
            
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
        2. 将向量和文本添加到存储
        3. 保存到磁盘（如果是JSON后端）
        
        参数：
            chunk: 要添加的文档文本块
        """
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            vector = self.embedding_service.get_vector(chunk)
            doc_id = f"doc_{len(self._ids)}"
            self._ids.append(doc_id)
            self._collection.add(
                embeddings=[vector],
                documents=[chunk],
                ids=[doc_id]
            )
        else:
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
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            vectors = [self.embedding_service.get_vector(chunk) for chunk in chunks]
            start_id = len(self._ids)
            doc_ids = [f"doc_{start_id + i}" for i in range(len(chunks))]
            self._ids.extend(doc_ids)
            
            self._collection.add(
                embeddings=vectors,
                documents=list(chunks),
                ids=doc_ids
            )
        else:
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
        results = self.search_with_scores(query_vector, k)
        return [doc for doc, _ in results]

    def search_with_scores(self, query_vector: List[float], k: int = 3) -> List[tuple]:
        """
        根据查询向量搜索最相关的 k 个文档，并返回相似度分数。
        
        参数：
            query_vector: 查询文本的嵌入向量
            k: 返回的最相关文档数量，默认为 3
            
        返回：
            (文档文本, 相似度分数) 的元组列表，按相似度从高到低排序
        """
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            results = self._collection.query(
                query_embeddings=[query_vector],
                n_results=k,
                include=["documents", "distances"]
            )
            
            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            # ChromaDB 的距离是欧氏距离，需要转换为相似度
            # 对于余弦相似度，距离越小越相似
            similarities = [1 / (1 + d) for d in distances]
            
            return list(zip(documents, similarities))
        else:
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
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            self._chroma_client.delete_collection(name=self.collection_name)
            self._ids = []
            # 重新创建集合
            self._collection = self._chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=None,
                metadata={"hnsw:space": "cosine"}
            )
        else:
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
        if self.backend == "chroma" and CHROMADB_AVAILABLE:
            return self._collection.count()
        else:
            return len(self.documents)
