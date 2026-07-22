"""MockParser - Mock 模式下的文档解析器"""
from parser import ParserAdapter


class MockParser(ParserAdapter):
    """Mock 解析器 — 返回固定演示数据，用于无 PPT 文件时的流程验证"""

    async def parse(self, file_path: str) -> list[dict]:
        """返回 Mock 课程数据"""
        return [
            {
                "page": 1,
                "title": "课程概述",
                "content": "本课程介绍计算机系统的基本组成和工作原理。",
            },
            {
                "page": 2,
                "title": "数据表示",
                "content": "二进制、十六进制与数值转换方法。",
            },
            {
                "page": 3,
                "title": "指令系统",
                "content": "指令格式、寻址方式与指令执行过程。",
            },
            {
                "page": 4,
                "title": "处理器设计",
                "content": "数据通路、控制器与流水线技术。",
            },
            {
                "page": 5,
                "title": "存储层次",
                "content": "Cache、主存与虚拟存储器的层次结构。",
            },
        ]
