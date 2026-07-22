"""测试：向量数据库"""
import asyncio

import pytest

from knowledge.embedding import MockEmbedding
from knowledge.vector_store import (
    MockVectorStore,
    VectorStoreProvider,
    get_vector_store,
)
from knowledge.retriever import Retriever


class TestMockVectorStore:
    """MockVectorStore 基本操作"""

    def test_add_and_search(self):
        store = MockVectorStore(dim=4)
        emb = MockEmbedding(dim=4)

        # 写入 3 条知识
        chunks = [
            {"chunk_id": "chk-01", "page": 1, "title": "Cache", "content": "Cache 提高访问速度"},
            {"chunk_id": "chk-02", "page": 2, "title": "CPU", "content": "CPU 执行指令"},
            {"chunk_id": "chk-03", "page": 3, "title": "内存", "content": "内存存储数据"},
        ]
        texts = [c["content"] for c in chunks]
        vecs = asyncio.run(emb.embed(texts))
        ids = asyncio.run(store.add(vecs, chunks))
        assert ids == ["chk-01", "chk-02", "chk-03"]

        # 检索
        query_vec = asyncio.run(emb.embed_single("Cache 提高访问速度"))
        results = asyncio.run(store.search(query_vec, top_k=2))
        assert len(results) == 2
        assert results[0]["id"] == "chk-01"  # 自己的向量最相似
        assert "score" in results[0]
        assert results[0]["metadata"]["title"] == "Cache"

    def test_search_empty_store(self):
        store = MockVectorStore(dim=4)
        results = asyncio.run(store.search([0.1, 0.2, 0.3, 0.4]))
        assert results == []

    def test_delete_removes_vector(self):
        store = MockVectorStore(dim=4)
        emb = MockEmbedding(dim=4)

        chunks = [{"chunk_id": "chk-del", "page": 1, "title": "X", "content": "待删除"}]
        vecs = asyncio.run(emb.embed(["待删除"]))
        asyncio.run(store.add(vecs, chunks))

        asyncio.run(store.delete(["chk-del"]))
        query_vec = asyncio.run(emb.embed_single("待删除"))
        results = asyncio.run(store.search(query_vec))
        assert results == []

    def test_top_k_exceeds_total(self):
        """请求的 top_k 超过总数时返回全部"""
        store = MockVectorStore(dim=4)
        emb = MockEmbedding(dim=4)
        chunks = [{"chunk_id": f"chk-{i}", "page": i, "title": f"T{i}", "content": f"C{i}"} for i in range(3)]
        vecs = asyncio.run(emb.embed([c["content"] for c in chunks]))
        asyncio.run(store.add(vecs, chunks))

        query_vec = asyncio.run(emb.embed_single("test"))
        results = asyncio.run(store.search(query_vec, top_k=10))
        assert len(results) == 3


class TestVectorStoreProvider:
    """抽象基类"""

    def test_base_raises_not_implemented(self):
        base = VectorStoreProvider()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.add([[0.1]], [{}]))
        with pytest.raises(NotImplementedError):
            asyncio.run(base.search([0.1]))
        with pytest.raises(NotImplementedError):
            asyncio.run(base.delete(["x"]))


class TestGetVectorStore:
    """工厂函数"""

    def test_default_returns_mock_store(self):
        store = get_vector_store(dim=64)
        assert isinstance(store, MockVectorStore)


class TestRetriever:
    """Retriever 端到端流程"""

    def test_retrieve_returns_matching_chunks(self):
        emb = MockEmbedding(dim=64)
        store = MockVectorStore(dim=64)
        retriever = Retriever(emb, store)

        # 存入知识
        chunks = [
            {"chunk_id": "chk-a", "page": 1, "title": "概述", "content": "Python 是一门编程语言", "source_file": "test.pptx"},
            {"chunk_id": "chk-b", "page": 2, "title": "变量", "content": "变量用于存储数据", "source_file": "test.pptx"},
        ]
        asyncio.run(retriever.add_chunks(chunks))

        # 检索
        results = asyncio.run(retriever.retrieve("Python 是一门编程语言", top_k=1))
        assert len(results) == 1
        assert results[0]["metadata"]["chunk_id"] == "chk-a"
        assert results[0]["metadata"]["source_file"] == "test.pptx"
