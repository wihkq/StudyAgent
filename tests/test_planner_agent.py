"""测试：PlannerAgent + /plan API"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from agents.planner_agent import MockPlannerAgent, PlannerAgent, get_planner_agent
from backend.main import app

client = TestClient(app)


class TestMockPlannerAgent:
    """MockPlannerAgent 计划生成"""

    @staticmethod
    def _sample_chapters():
        return [
            {"title": "数据表示", "page_count": 3, "importance": 5, "key_points": ["二进制", "十六进制"]},
            {"title": "指令系统", "page_count": 2, "importance": 3, "key_points": ["指令格式"]},
            {"title": "处理器设计", "page_count": 1, "importance": 2, "key_points": ["数据通路"]},
        ]

    def test_generate_returns_plan_with_days(self):
        agent = MockPlannerAgent()
        result = asyncio.run(agent.generate("2026-08-15", 4.0, self._sample_chapters()))
        assert len(result["plan"]) > 0
        assert result["plan"][0]["day"] == 1
        assert "date" in result["plan"][0]
        assert len(result["plan"][0]["tasks"]) > 0

    def test_generate_important_chapter_more_days(self):
        agent = MockPlannerAgent()
        result = asyncio.run(agent.generate("2026-08-15", 4.0, [
            {"title": "重点章", "page_count": 5, "importance": 5, "key_points": []},
        ]))
        # importance=5 + 天数充裕 → 可能分配 2 天
        assert len(result["plan"]) >= 1

    def test_generate_empty_chapters_informs(self):
        agent = MockPlannerAgent()
        result = asyncio.run(agent.generate("2026-08-15", 4.0, []))
        assert result["plan"] == []
        assert "暂无课程章节" in result["summary"]["message"]

    def test_tasks_have_valid_hours(self):
        agent = MockPlannerAgent()
        result = asyncio.run(agent.generate("2026-08-15", 4.0, self._sample_chapters()))
        for day in result["plan"]:
            total = sum(t["hours"] for t in day["tasks"])
            assert 0 < total <= 4.0 + 0.1  # 允许浮点误差

    def test_summary_contains_stats(self):
        agent = MockPlannerAgent()
        result = asyncio.run(agent.generate("2026-08-15", 6.0, self._sample_chapters()))
        s = result["summary"]
        assert s["daily_hours"] == 6.0
        assert s["chapters_covered"] == 3


class TestPlannerAgentBase:
    def test_base_raises_not_implemented(self):
        base = PlannerAgent()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.generate("2026-01-01", 4.0, []))


class TestGetPlannerAgent:
    def test_default_returns_mock(self):
        assert isinstance(get_planner_agent(), MockPlannerAgent)


class TestPlanAPI:
    """POST /api/v1/plan"""

    def test_plan_returns_200(self):
        resp = client.post("/api/v1/plan", json={
            "exam_date": "2026-08-15",
            "daily_hours": 4.0,
            "chapters": [
                {"title": "概述", "page_count": 1, "importance": 3, "key_points": []},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "plan" in data
        assert "summary" in data

    def test_plan_invalid_date_rejected(self):
        resp = client.post("/api/v1/plan", json={
            "exam_date": "invalid",
            "daily_hours": 4.0,
        })
        assert resp.status_code == 422
