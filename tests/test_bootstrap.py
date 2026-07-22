"""测试：项目骨架可正常启动"""
import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealthCheck:
    """服务健康检查"""

    def test_root_returns_status(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "StudyAgent"
        assert data["status"] == "running"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_api_v1_status(self):
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_version"] == "v1"
        assert data["status"] == "ok"

    def test_api_404_on_unknown_route(self):
        """未定义路由返回 404 而非 500"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestConfig:
    """配置加载"""

    def test_settings_defaults(self):
        from config import Settings
        s = Settings()
        assert s.parser_mode == "mock"
        assert s.llm_mode == "mock"
        assert s.vector_mode == "mock_faiss"
        assert s.host == "0.0.0.0"
        assert s.port == 8000

    def test_settings_env_override(self):
        """修改环境变量后新建 Settings 实例应反映变更"""
        from config import Settings

        os.environ["LLM_MODE"] = "openai_compatible"
        os.environ["PORT"] = "9999"
        try:
            s = Settings()
            assert s.llm_mode == "openai_compatible"
            assert s.port == 9999
        finally:
            os.environ.pop("LLM_MODE", None)
            os.environ.pop("PORT", None)


class TestProviderInterfaces:
    """Provider/Adapter 接口定义正确"""

    def test_embedding_provider_interface(self):
        from knowledge.embedding import EmbeddingProvider
        assert hasattr(EmbeddingProvider, "embed")
        assert hasattr(EmbeddingProvider, "embed_single")

    def test_embedding_provider_raises(self):
        """调用未实现的 embed 应抛出 NotImplementedError"""
        from knowledge.embedding import EmbeddingProvider
        import asyncio
        with pytest.raises(NotImplementedError):
            asyncio.run(EmbeddingProvider().embed(["test"]))

    def test_vector_store_interface(self):
        from knowledge.vector_store import VectorStoreProvider
        assert hasattr(VectorStoreProvider, "add")
        assert hasattr(VectorStoreProvider, "search")
        assert hasattr(VectorStoreProvider, "delete")

    def test_vector_store_raises(self):
        """调用未实现的 search 应抛出 NotImplementedError"""
        from knowledge.vector_store import VectorStoreProvider
        import asyncio
        with pytest.raises(NotImplementedError):
            asyncio.run(VectorStoreProvider().search([0.1], top_k=5))

    def test_retriever_interface(self):
        from knowledge.retriever import Retriever
        assert hasattr(Retriever, "retrieve")

    def test_parser_adapter_interface(self):
        from parser import ParserAdapter
        assert hasattr(ParserAdapter, "parse")

    def test_parser_adapter_raises(self):
        """调用未实现的 parse 应抛出 NotImplementedError"""
        from parser import ParserAdapter
        import asyncio
        with pytest.raises(NotImplementedError):
            asyncio.run(ParserAdapter().parse("/fake/path.pptx"))
