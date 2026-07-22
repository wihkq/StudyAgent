"""测试：DocumentAgent 课程资料分析"""
import asyncio

import pytest

from agents.document_agent import DocumentAgent, MockDocumentAgent, get_document_agent


class TestMockDocumentAgent:
    """MockDocumentAgent 分析逻辑"""

    @staticmethod
    def _sample_pages():
        return [
            {"page": 1, "title": "课程概述", "content": "本课程介绍计算机系统的基本组成。重点掌握整体架构。"},
            {"page": 2, "title": "数据表示", "content": "二进制是计算机的核心基础。必考数值转换方法。"},
            {"page": 3, "title": "数据表示", "content": "十六进制与二进制的转换公式。核心考点。"},
            {"page": 4, "title": "指令系统", "content": "指令格式包括操作码和地址码。注意寻址方式。"},
            {"page": 5, "title": "处理器设计", "content": "数据通路和控制器是关键组件。"},
        ]

    def test_analyze_returns_course_name(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages(), "计算机组成"))
        assert result["course_name"] == "计算机组成"

    def test_analyze_groups_chapters_by_title(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages()))
        # 5 页，但 "数据表示" 出现 2 次 → 4 个章节
        assert len(result["chapters"]) == 4

    def test_analyze_data_representation_has_two_pages(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages()))
        dr_chapter = [c for c in result["chapters"] if c["title"] == "数据表示"][0]
        assert dr_chapter["page_count"] == 2
        assert dr_chapter["pages"] == [2, 3]

    def test_importance_range_1_to_5(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages()))
        for ch in result["chapters"]:
            assert 1 <= ch["importance"] <= 5

    def test_keywords_boost_importance(self):
        """包含重点关键词的章节重要程度更高"""
        agent = MockDocumentAgent()
        # "数据表示" 含 重点/核心/必考 → 应高于普通章节
        result = asyncio.run(agent.analyze(self._sample_pages()))
        dr = [c for c in result["chapters"] if c["title"] == "数据表示"][0]
        overview = [c for c in result["chapters"] if c["title"] == "课程概述"][0]
        assert dr["importance"] >= overview["importance"]

    def test_key_points_extracted(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages()))
        for ch in result["chapters"]:
            assert len(ch["key_points"]) <= 5
            for kp in ch["key_points"]:
                assert len(kp) > 5  # 至少有意义

    def test_empty_pages_returns_empty(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze([], "空课程"))
        assert result["chapters"] == []
        assert result["course_name"] == "空课程"

    def test_knowledge_map_has_stats(self):
        agent = MockDocumentAgent()
        result = asyncio.run(agent.analyze(self._sample_pages()))
        km = result["knowledge_map"]
        assert km["total_chapters"] == 4
        assert km["total_pages"] == 5
        assert 1.0 <= km["average_importance"] <= 5.0


class TestDocumentAgent:
    """抽象基类"""

    def test_base_raises_not_implemented(self):
        base = DocumentAgent()
        with pytest.raises(NotImplementedError):
            asyncio.run(base.analyze([]))


class TestGetDocumentAgent:
    """工厂函数"""

    def test_default_returns_mock(self):
        agent = get_document_agent()
        assert isinstance(agent, MockDocumentAgent)
