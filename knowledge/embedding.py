"""EmbeddingProvider - 文本向量化接口

可替换实现：MockEmbedding / OpenAIEmbedding / BGEEmbedding
"""
# TODO: Issue-007 实现


class EmbeddingProvider:
    """向量化抽象基类"""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """将文本列表转换为向量列表"""
        raise NotImplementedError

    async def embed_single(self, text: str) -> list[float]:
        """将单个文本转换为向量"""
        raise NotImplementedError
