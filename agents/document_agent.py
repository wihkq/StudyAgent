"""DocumentAgent - 课程资料分析

职责：分析解析后的 PPT 页面，提取课程结构、核心知识点、重点标记。
输出：课程知识地图。
"""
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

# 常见重点标记词
IMPORTANCE_KEYWORDS = [
    "重点", "核心", "必考", "考点", "总结", "注意", "关键",
    "重要", "必须掌握", "难点", "高频", "公式", "定义",
]


class DocumentAgent:
    """课程资料分析 Agent 抽象基类"""

    async def analyze(self, pages: list[dict], course_name: str = "") -> dict:
        """分析课程页面，返回结构化知识地图

        Args:
            pages: [{page, title, content}, ...]
            course_name: 课程名称

        Returns:
            {course_name, chapters: [{title, pages, importance, key_points}], knowledge_map}
        """
        raise NotImplementedError


class MockDocumentAgent(DocumentAgent):
    """Mock DocumentAgent — 基于规则分析，无需 LLM"""

    async def analyze(self, pages: list[dict], course_name: str = "") -> dict:
        if not pages:
            return {"course_name": course_name, "chapters": [], "knowledge_map": {}}

        # 1. 按标题分组形成章节
        chapters = self._group_by_title(pages)

        # 2. 计算每章重要程度
        for ch in chapters:
            ch["importance"] = self._calc_importance(ch)
            ch["key_points"] = self._extract_key_points(ch["pages_data"])

        # 3. 构建知识地图
        knowledge_map = self._build_knowledge_map(chapters)

        return {
            "course_name": course_name,
            "chapters": [
                {
                    "title": ch["title"],
                    "pages": ch["pages"],
                    "page_count": ch["page_count"],
                    "importance": ch["importance"],
                    "key_points": ch["key_points"],
                }
                for ch in chapters
            ],
            "knowledge_map": knowledge_map,
        }

    def _group_by_title(self, pages: list[dict]) -> list[dict]:
        """按页面标题分组"""
        groups = []
        seen = set()
        for p in pages:
            title = p.get("title", "未命名")
            if title not in seen:
                seen.add(title)
                groups.append({
                    "title": title,
                    "pages": [p["page"]],
                    "page_count": 1,
                    "pages_data": [p],
                })
            else:
                for g in groups:
                    if g["title"] == title:
                        g["pages"].append(p["page"])
                        g["page_count"] += 1
                        g["pages_data"].append(p)
                        break
        return groups

    def _calc_importance(self, chapter: dict) -> int:
        """计算章节重要程度 (1-5)"""
        score = 1
        all_text = " ".join(p.get("content", "") for p in chapter["pages_data"])

        # 因素1：内容长度
        if len(all_text) > 500:
            score += 1
        if len(all_text) > 1000:
            score += 1

        # 因素2：关键词命中
        keyword_hits = sum(1 for kw in IMPORTANCE_KEYWORDS if kw in all_text)
        if keyword_hits >= 1:
            score += 1
        if keyword_hits >= 3:
            score += 1

        return min(score, 5)

    def _extract_key_points(self, pages_data: list[dict]) -> list[str]:
        """从页面中提取知识点"""
        points = []
        for p in pages_data:
            content = p.get("content", "")
            if content:
                # 取第一句作为知识点
                first_sentence = re.split(r"[。！？\n]", content)[0].strip()
                if first_sentence and len(first_sentence) > 5:
                    points.append(first_sentence)
        return points[:5]  # 最多 5 个知识点

    def _build_knowledge_map(self, chapters: list[dict]) -> dict:
        """构建简易知识地图"""
        nodes = []
        for ch in chapters:
            stars = "★" * ch["importance"] + "☆" * (5 - ch["importance"])
            nodes.append({
                "title": ch["title"],
                "importance_stars": stars,
                "page_count": ch["page_count"],
                "key_points_count": len(ch["key_points"]),
            })
        return {
            "total_chapters": len(chapters),
            "total_pages": sum(ch["page_count"] for ch in chapters),
            "average_importance": round(
                sum(ch["importance"] for ch in chapters) / max(len(chapters), 1), 1
            ),
            "nodes": nodes,
        }


def get_document_agent() -> DocumentAgent:
    """工厂函数：根据 LLM_MODE 返回 DocumentAgent 实例"""
    from config.settings import Settings

    mode = Settings().llm_mode
    if mode in ("mock",):
        return MockDocumentAgent()
    elif mode == "kimi":
        # Kimi LLM Agent 占位 — 后续 Issue 实现
        logger.warning("LLM_MODE=kimi，但 DocumentAgent 尚未集成 LLM，回退 Mock")
        return MockDocumentAgent()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockDocumentAgent", mode)
        return MockDocumentAgent()
