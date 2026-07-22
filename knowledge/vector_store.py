"""VectorStoreProvider - 向量数据库接口

可替换实现：MockVectorStore / FAISSVectorStore / MilvusVectorStore
"""
# TODO: Issue-008 实现


class VectorStoreProvider:
    """向量存储抽象基类"""

    async def add(self, vectors: list[list[float]], metadata: list[dict]) -> list[str]:
        """存入向量，返回 ID 列表"""
        raise NotImplementedError

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """相似度搜索，返回 top_k 条 {id, metadata, score}"""
        raise NotImplementedError

    async def delete(self, ids: list[str]) -> None:
        """删除指定 ID 的向量"""
        raise NotImplementedError
