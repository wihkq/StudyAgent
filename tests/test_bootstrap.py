"""测试：项目骨架可正常启动"""
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


class TestConfig:
    """配置加载"""

    def test_settings_defaults(self):
        from config import settings
        assert settings.parser_mode == "mock"
        assert settings.llm_mode == "mock"
        assert settings.vector_mode == "mock_faiss"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000


class TestProviderInterfaces:
    """Provider/Adapter 接口定义正确"""

    def test_embedding_provider_interface(self):
        from knowledge.embedding import EmbeddingProvider
        assert hasattr(EmbeddingProvider, "embed")
        assert hasattr(EmbeddingProvider, "embed_single")

    def test_vector_store_interface(self):
        from knowledge.vector_store import VectorStoreProvider
        assert hasattr(VectorStoreProvider, "add")
        assert hasattr(VectorStoreProvider, "search")
        assert hasattr(VectorStoreProvider, "delete")

    def test_retriever_interface(self):
        from knowledge.retriever import Retriever
        assert hasattr(Retriever, "retrieve")

    def test_parser_adapter_interface(self):
        from parser.ppt_parser import ParserAdapter
        assert hasattr(ParserAdapter, "parse")
