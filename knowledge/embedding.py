"""EmbeddingProvider - 文本向量化接口

可替换实现：MockEmbedding / KimiEmbedding
"""
import hashlib
import logging

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
            val = int.from_bytes(digest[i:i+2], "big") / 65535.0
            values.append(round(val, 6))
        while len(values) < self.dim:
            values.append(0.0)
        return values[:self.dim]


class KimiEmbedding(EmbeddingProvider):
    """月之暗面 Kimi Embedding API

    兼容 OpenAI 格式，endpoint: /v1/embeddings
    """

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.moonshot.cn/v1",
        model: str = "moonshot-v1-8k",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise ValueError("Kimi API Key 未配置，请设置 LLM_API_KEY 环境变量")

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": texts},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    async def embed_single(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]


def get_embedding() -> EmbeddingProvider:
    """工厂函数：根据 LLM_MODE 返回 Embedding 实例

    模式:
      mock     — MockEmbedding（默认，免费本地）
      kimi     — KimiEmbedding（月之暗面 API）
      deepseek — DeepSeek Embedding（OpenAI 兼容，若无则回退 Mock）
    """
    from config.settings import Settings

    s = Settings()
    mode = s.llm_mode
    api_key = s.llm_api_key

    if mode == "mock":
        return MockEmbedding()
    elif mode in ("kimi", "deepseek"):
        if api_key:
            # DeepSeek 和 Kimi 都兼容 OpenAI Embedding 格式
            return KimiEmbedding(
                api_key=api_key,
                base_url=s.llm_api_base,
                model=s.llm_model,
            )
        else:
            logger.warning("LLM_MODE=%s 但 LLM_API_KEY 未配置，回退 MockEmbedding", mode)
            return MockEmbedding()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockEmbedding", mode)
        return MockEmbedding()


__all__ = ["EmbeddingProvider", "MockEmbedding", "KimiEmbedding", "get_embedding"]
