"""测试：ExaminerAgent + /exam API"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from agents.examiner_agent import MockExaminerAgent, ExaminerAgent, get_examiner_agent
from backend.main import app

client = TestClient(app)


class TestMockExaminerAgent:
    """MockExaminerAgent 出题和评分"""

    @staticmethod
    def _sample_chapters():
        return [
            {"title": "Cache", "page_count": 3, "importance": 5,
             "key_points": ["Cache 提高 CPU 访问速度", "局部性原理是 Cache 的基础", "三种映射方式"]},
            {"title": "CPU", "page_count": 2, "importance": 4,
             "key_points": ["CPU 执行指令的五个阶段", "流水线提高吞吐率"]},
        ]

    def test_generate_returns_questions(self):
        agent = MockExaminerAgent()
        result = asyncio.run(agent.generate_exam(self._sample_chapters(), 4))
        assert len(result["questions"]) == 4
        assert result["total"] == 4

    def test_generate_mix_of_types(self):
        agent = MockExaminerAgent()
        result = asyncio.run(agent.generate_exam(self._sample_chapters(), 6))
        types = {q["type"] for q in result["questions"]}
        assert "choice" in types
        assert "short_answer" in types

    def test_generate_empty_chapters(self):
        agent = MockExaminerAgent()
        result = asyncio.run(agent.generate_exam([], 5))
        assert result["questions"] == []

    def test_grade_correct_choice(self):
        agent = MockExaminerAgent()
        questions = [{"type": "choice", "question": "Q1", "answer": "A", "options": [], "keywords": []}]
        result = asyncio.run(agent.grade(questions, ["A"]))
        assert result["score"] == 1
        assert result["total"] == 1

    def test_grade_wrong_choice(self):
        agent = MockExaminerAgent()
        questions = [{"type": "choice", "question": "Q1", "answer": "A", "options": [], "keywords": []}]
        result = asyncio.run(agent.grade(questions, ["B"]))
        assert result["score"] == 0

    def test_grade_short_answer_keyword_match(self):
        agent = MockExaminerAgent()
        questions = [{
            "type": "short_answer", "question": "Q1", "answer": "Cache",
            "keywords": ["Cache", "局部性"], "explanation": ""
        }]
        result = asyncio.run(agent.grade(questions, ["Cache 利用局部性"]))
        assert result["score"] == 1

    def test_grade_mismatched_count_raises(self):
        agent = MockExaminerAgent()
        questions = [{"type": "choice", "question": "Q1", "answer": "A", "options": [], "keywords": []}]
        with pytest.raises(ValueError, match="不匹配"):
            asyncio.run(agent.grade(questions, ["A", "B"]))


class TestExaminerAgentBase:
    def test_base_raises(self):
        base = ExaminerAgent()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.generate_exam([]))


class TestGradeAPI:
    """答案数不匹配校验"""

    def test_mismatched_length_returns_422(self):
        resp = client.post("/api/v1/exam/grade", json={
            "questions": [{"type": "choice", "question": "Q", "answer": "A", "options": [], "keywords": []}],
            "answers": ["A", "B"],  # 多一个答案
        })
        assert resp.status_code == 422


class TestGetExaminerAgent:
    def test_default_returns_mock(self):
        assert isinstance(get_examiner_agent(), MockExaminerAgent)


class TestExamAPI:
    """POST /api/v1/exam/*"""

    def test_generate_returns_200(self):
        resp = client.post("/api/v1/exam/generate", json={
            "chapters": [
                {"title": "T", "page_count": 1, "importance": 3,
                 "key_points": ["测试知识点"]},
            ],
            "question_count": 2,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 1  # 只有 1 个知识点，最多 1 题

    def test_grade_returns_200(self):
        resp = client.post("/api/v1/exam/grade", json={
            "questions": [{"type": "choice", "question": "Q", "answer": "A", "options": [], "keywords": []}],
            "answers": ["A"],
        })
        assert resp.status_code == 200
        assert resp.json()["score"] == 1
