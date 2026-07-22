"""MockParser - Mock 模式下的文档解析器"""
from parser import ParserAdapter


class MockParser(ParserAdapter):
    """Mock 解析器 — 返回通用演示数据，用于无 PPT 文件时的流程验证"""

    async def parse(self, file_path: str) -> list[dict]:
        """返回 Mock 课程数据（通用抽象内容，不含具体课程知识）"""
        return [
            {
                "page": 1,
                "title": "第一章：概述",
                "content": "本章介绍课程的核心概念和学习目标，建立整体知识框架。",
            },
            {
                "page": 2,
                "title": "第二章：基础知识",
                "content": "深入讲解基础理论和关键原理，为后续章节打下基础。",
            },
            {
                "page": 3,
                "title": "第三章：核心方法",
                "content": "详细阐述本课程的核心方法论和技术手段。",
            },
            {
                "page": 4,
                "title": "第四章：进阶应用",
                "content": "结合实际案例，展示理论知识在实际问题中的应用。",
            },
            {
                "page": 5,
                "title": "第五章：总结回顾",
                "content": "梳理课程重点内容，构建完整的知识体系。",
            },
        ]
