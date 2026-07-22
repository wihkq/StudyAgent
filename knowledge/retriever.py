"""Retriever - 知识检索

组合 EmbeddingProvider + VectorStoreProvider，
将用户查询转换为向量并检索相关 Chunk。
"""


class Retriever:
    """知识检索器 — 查询向量化 + Top-K 检索"""

    def __init__(self, embedding_provider, vector_store):
        self.embedding = embedding_provider
        self.store = vector_store

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """检索与查询最相关的知识 Chunk

        Args:
            query: 用户查询文本
            top_k: 返回结果数量

        Returns:
            [{id, metadata: {chunk_id, page, title, content, source_file}, score}, ...]
        """
        query_vec = await self.embedding.embed_single(query)
        results = await self.store.search(query_vec, top_k=top_k)
        return results

    async def add_chunks(self, chunks: list[dict]) -> list[str]:
        """将 Chunk 列表存入向量数据库

        Args:
            chunks: [{chunk_id, page, title, content, source_file}, ...]

        Returns:
            存入的 chunk_id 列表
        """
        texts = [c["content"] for c in chunks]
        vectors = await self.embedding.embed(texts)
        ids = await self.store.add(vectors, chunks)
        return ids
