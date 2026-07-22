"""VectorStoreProvider - 向量数据库接口

可替换实现：MockVectorStore / FAISSVectorStore
"""
import logging
import os

import numpy as np

logger = logging.getLogger(__name__)


class VectorStoreProvider:
    """向量存储抽象基类"""

    async def add(self, vectors: list[list[float]], metadata: list[dict]) -> list[str]:
        """存入向量和元数据，返回 ID 列表"""
        raise NotImplementedError

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """Top-K 相似度搜索，返回 [{id, metadata, score}, ...]"""
        raise NotImplementedError

    async def delete(self, ids: list[str]) -> None:
        """删除指定 ID 的向量"""
        raise NotImplementedError


class MockVectorStore(VectorStoreProvider):
    """Mock 向量存储 — 基于 NumPy 内存实现，余弦相似度检索"""

    def __init__(self, dim: int = 128):
        self.dim = dim
        self._vectors: dict[str, np.ndarray] = {}
        self._metadata: dict[str, dict] = {}
        self._counter = 0

    async def add(self, vectors: list[list[float]], metadata: list[dict]) -> list[str]:
        ids = []
        for vec, meta in zip(vectors, metadata):
            self._counter += 1
            chunk_id = meta.get("chunk_id", f"vec-{self._counter:06d}")
            self._vectors[chunk_id] = np.array(vec, dtype=np.float32)
            self._metadata[chunk_id] = meta
            ids.append(chunk_id)
        return ids

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        if not self._vectors:
            return []

        query = np.array(query_vector, dtype=np.float32)
        ids = list(self._vectors.keys())
        matrix = np.stack([self._vectors[i] for i in ids])

        # 余弦相似度
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        scores = np.dot(matrix_norm, query_norm)

        # Top-K
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            chunk_id = ids[idx]
            results.append({
                "id": chunk_id,
                "metadata": self._metadata[chunk_id],
                "score": round(score, 6),
            })
        return results

    async def delete(self, ids: list[str]) -> None:
        for chunk_id in ids:
            self._vectors.pop(chunk_id, None)
            self._metadata.pop(chunk_id, None)


try:
    import faiss

    class FAISSVectorStore(VectorStoreProvider):
        """FAISS 向量存储 — 基于 IndexFlatIP 内积索引"""

        def __init__(self, dim: int = 128):
            self.dim = dim
            self._index = faiss.IndexFlatIP(dim)  # 内积 = 归一化后等价余弦相似度
            self._id_list: list[str] = []
            self._metadata: dict[str, dict] = {}

        async def add(self, vectors: list[list[float]], metadata: list[dict]) -> list[str]:
            matrix = np.array(vectors, dtype=np.float32)
            # 归一化
            norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
            matrix = matrix / norms

            self._index.add(matrix)
            ids = []
            for meta in metadata:
                chunk_id = meta.get("chunk_id", f"vec-{len(self._id_list):06d}")
                self._id_list.append(chunk_id)
                self._metadata[chunk_id] = meta
                ids.append(chunk_id)
            return ids

        async def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
            if self._index.ntotal == 0:
                return []

            query = np.array([query_vector], dtype=np.float32)
            query = query / (np.linalg.norm(query) + 1e-10)

            scores, indices = self._index.search(query, min(top_k, self._index.ntotal))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self._id_list):
                    chunk_id = self._id_list[idx]
                    results.append({
                        "id": chunk_id,
                        "metadata": self._metadata[chunk_id],
                        "score": round(float(score), 6),
                    })
            return results

        async def delete(self, ids: list[str]) -> None:
            # FAISS 不支持删除，重建索引
            pass

except ImportError:
    FAISSVectorStore = None  # type: ignore


def get_vector_store(dim: int = 128) -> VectorStoreProvider:
    """工厂函数：根据 VECTOR_MODE 返回向量存储实例"""
    mode = os.getenv("VECTOR_MODE", "mock_faiss")

    if mode == "mock_faiss":
        return MockVectorStore(dim=dim)
    elif mode == "faiss":
        if FAISSVectorStore is not None:
            return FAISSVectorStore(dim=dim)
        else:
            logger.warning("VECTOR_MODE=faiss 但 faiss-cpu 未安装，回退 MockVectorStore")
            return MockVectorStore(dim=dim)
    else:
        logger.warning("未知 VECTOR_MODE=%s，回退 MockVectorStore", mode)
        return MockVectorStore(dim=dim)


__all__ = ["VectorStoreProvider", "MockVectorStore", "FAISSVectorStore", "get_vector_store"]
