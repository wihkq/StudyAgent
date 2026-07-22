"""Retriever - 知识检索

组合 EmbeddingProvider + VectorStoreProvider，
将用户查询转换为向量并检索相关 Chunk。
"""
# TODO: Issue-008 实现


class Retriever:
    """知识检索器"""

    def __init__(self, embedding_provider, vector_store):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """检索与查询最相关的知识 Chunk"""
        raise NotImplementedError
