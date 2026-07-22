"""测试：TutorAgent + /chat API"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from agents.tutor_agent import MockTutorAgent, TutorAgent, get_tutor_agent
from backend.main import app

client = TestClient(app)


class TestMockTutorAgent:
    """MockTutorAgent 回答逻辑"""

    @staticmethod
    def _sample_chunks():
        return [
            {
                "id": "chk-01",
                "metadata": {
                    "chunk_id": "chk-01", "page": 15, "title": "Cache",
                    "content": "Cache 利用局部性原理提高 CPU 访问速度，减少访问主存次数。",
                    "source_file": "计算机组成.pptx",
                },
                "score": 0.95,
            },
            {
                "id": "chk-02",
                "metadata": {
                    "chunk_id": "chk-02", "page": 16, "title": "Cache 映射",
                    "content": "直接映射、全相联映射和组相联映射是三种主要方式。",
                    "source_file": "计算机组成.pptx",
                },
                "score": 0.82,
            },
        ]

    def test_answer_with_chunks_includes_sources(self):
        agent = MockTutorAgent()
        result = asyncio.run(agent.answer("Cache 是什么？", self._sample_chunks()))
        assert "Cache" in result["answer"]
        assert len(result["sources"]) == 2
        assert result["sources"][0]["page"] == 15
        assert result["sources"][0]["source_file"] == "计算机组成.pptx"

    def test_answer_with_chunks_cites_page_numbers(self):
        agent = MockTutorAgent()
        result = asyncio.run(agent.answer("Cache", self._sample_chunks()))
        assert "15" in result["answer"] or "第 15 页" in result["answer"]

    def test_answer_empty_chunks_informs_user(self):
        agent = MockTutorAgent()
        result = asyncio.run(agent.answer("不存在的内容", []))
        assert "未找到" in result["answer"]
        assert result["sources"] == []

    def test_answer_top_3_only(self):
        """超过 3 个 chunk 时只取 top-3"""
        chunks = [self._sample_chunks()[0]] * 5  # 5 个相同 chunk
        agent = MockTutorAgent()
        result = asyncio.run(agent.answer("test", chunks))
        assert len(result["sources"]) == 3


class TestTutorAgentBase:
    """抽象基类"""

    def test_base_raises_not_implemented(self):
        base = TutorAgent()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.answer("test", []))


class TestGetTutorAgent:
    """工厂函数"""

    def test_default_returns_mock(self):
        agent = get_tutor_agent()
        assert isinstance(agent, MockTutorAgent)


class TestChatAPI:
    """POST /api/v1/chat"""

    def test_chat_empty_knowledge_base(self):
        """知识库为空时告知用户"""
        resp = client.post("/api/v1/chat", json={"question": "什么是Cache？"})
        assert resp.status_code == 200
        data = resp.json()
        assert "未找到" in data["answer"]

    def test_chat_requires_question(self):
        resp = client.post("/api/v1/chat", json={"top_k": 5})
        assert resp.status_code == 422
        assert resp.json()["error_code"] == "VALIDATION_ERROR"

    def test_chat_empty_question_rejected(self):
        resp = client.post("/api/v1/chat", json={"question": ""})
        assert resp.status_code == 422
        assert resp.json()["error_code"] == "VALIDATION_ERROR"

    def test_chat_validates_top_k_range(self):
        resp = client.post("/api/v1/chat", json={"question": "test", "top_k": 0})
        assert resp.status_code == 422
        assert resp.json()["error_code"] == "VALIDATION_ERROR"
        resp = client.post("/api/v1/chat", json={"question": "test", "top_k": 100})
        assert resp.status_code == 422
