"""测试：Embedding 文本向量化"""
import asyncio

import pytest

from knowledge.embedding import (
    EmbeddingProvider,
    KimiEmbedding,
    MockEmbedding,
    get_embedding,
)


class TestMockEmbedding:
    """MockEmbedding 行为"""

    def test_embed_single_returns_correct_dim(self):
        emb = MockEmbedding(dim=128)
        vec = asyncio.run(emb.embed_single("测试文本"))
        assert len(vec) == 128
        assert all(0.0 <= v <= 1.0 for v in vec)

    def test_embed_batch_returns_all_vectors(self):
        emb = MockEmbedding(dim=64)
        texts = ["A", "B", "C"]
        vecs = asyncio.run(emb.embed(texts))
        assert len(vecs) == 3
        assert all(len(v) == 64 for v in vecs)

    def test_same_text_same_vector(self):
        """相同文本应产生相同向量（确定性）"""
        emb = MockEmbedding()
        v1 = asyncio.run(emb.embed_single("hello"))
        v2 = asyncio.run(emb.embed_single("hello"))
        assert v1 == v2

    def test_different_texts_different_vectors(self):
        """不同文本应产生不同向量"""
        emb = MockEmbedding()
        v1 = asyncio.run(emb.embed_single("hello"))
        v2 = asyncio.run(emb.embed_single("world"))
        assert v1 != v2

    def test_empty_string_returns_vector(self):
        emb = MockEmbedding()
        vec = asyncio.run(emb.embed_single(""))
        assert len(vec) == 128

    def test_custom_dim(self):
        emb = MockEmbedding(dim=256)
        vec = asyncio.run(emb.embed_single("test"))
        assert len(vec) == 256


class TestEmbeddingProvider:
    """抽象基类"""

    def test_base_raises_not_implemented(self):
        base = EmbeddingProvider()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.embed_single("test"))
        with pytest.raises(NotImplementedError):
            asyncio.run(base.embed(["test"]))


class TestGetEmbedding:
    """工厂函数"""

    def test_default_returns_mock_embedding(self):
        emb = get_embedding()
        assert isinstance(emb, MockEmbedding)


class TestKimiEmbedding:
    """KimiEmbedding 接口"""

    def test_kimi_requires_api_key(self):
        """无 API Key 时 embed 应抛异常"""
        kimi = KimiEmbedding(api_key="")
        with pytest.raises(ValueError, match="API Key"):
            asyncio.run(kimi.embed_single("test"))

    def test_kimi_has_correct_defaults(self):
        kimi = KimiEmbedding(api_key="sk-test")
        assert kimi.base_url == "https://api.moonshot.cn/v1"
        assert kimi.model == "moonshot-v1-8k"
