"""EmbeddingProvider - 文本向量化接口

可替换实现：MockEmbedding / OpenAIEmbedding / BGEEmbedding
"""
import hashlib
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """向量化抽象基类"""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """将文本列表转换为向量列表"""
        raise NotImplementedError

    async def embed_single(self, text: str) -> list[float]:
        """将单个文本转换为向量"""
        raise NotImplementedError


class MockEmbedding(EmbeddingProvider):
    """Mock Embedding — 基于文本 hash 生成确定性向量，维度 128"""

    def __init__(self, dim: int = 128):
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_vector(t) for t in texts]

    async def embed_single(self, text: str) -> list[float]:
        return self._hash_vector(text)

    def _hash_vector(self, text: str) -> list[float]:
        """用 SHAKE-256 将文本扩展为 dim 维的归一化向量"""
        digest = hashlib.shake_256(text.encode("utf-8")).digest(self.dim * 2)
        values = []
        for i in range(0, len(digest), 2):
            # 两个字节 → 0~1 之间的浮点数
            val = int.from_bytes(digest[i:i+2], "big") / 65535.0
            values.append(round(val, 6))
        # 补齐不足 dim 的情况
        while len(values) < self.dim:
            values.append(0.0)
        return values[:self.dim]


def get_embedding() -> EmbeddingProvider:
    """工厂函数：根据 LLM_MODE 返回 Embedding 实例"""
    mode = os.getenv("LLM_MODE", "mock")
    if mode == "mock":
        return MockEmbedding()
    elif mode in ("openai_compatible", "live"):
        # OpenAI Embedding 占位 — 真实集成留到后续
        logger.warning("LLM_MODE=%s 已配置，但 OpenAI Embedding 尚未集成，回退 MockEmbedding", mode)
        return MockEmbedding()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockEmbedding", mode)
        return MockEmbedding()


__all__ = ["EmbeddingProvider", "MockEmbedding", "get_embedding"]
