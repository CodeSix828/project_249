import numpy as np
from ...llms.deepseek_embedding import DeepseekEmbedding

class EmbeddingService():
    def __init__(self):
        self.embedding = DeepseekEmbedding()

    def get_vector(self, chunk):
        vector = self.embedding.get_embedding(chunk)
        return vector

    def get_similarity(self, vector1, vector2):
        """计算两个向量的余弦相似度"""
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        return dot_product / magnitude if magnitude else 0
