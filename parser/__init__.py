"""Parser package - 文档解析适配器

可替换实现：MockParser / PptxParser / PdfParser
"""


class ParserAdapter:
    """文档解析抽象基类"""

    async def parse(self, file_path: str) -> list[dict]:
        """解析文档，返回 [{page, title, content}, ...]"""
        raise NotImplementedError


__all__ = ["ParserAdapter"]
