"""Parser package - 文档解析适配器

可替换实现：MockParser / PptxParser / PdfParser
"""


class ParserAdapter:
    """文档解析抽象基类"""

    async def parse(self, file_path: str) -> list[dict]:
        """解析文档，返回 [{page, title, content}, ...]"""
        raise NotImplementedError


def get_parser(file_path: str = "") -> "ParserAdapter":
    """工厂函数：根据全局配置和文件类型返回合适的解析器"""
    import os
    from pathlib import Path

    parser_mode = os.getenv("PARSER_MODE", "mock")

    if parser_mode == "mock":
        from parser.mock_parser import MockParser
        return MockParser()

    # live 模式：按扩展名选择解析器
    ext = Path(file_path).suffix.lower() if file_path else ""
    if ext == ".pptx":
        from parser.ppt_parser import PptxParser
        return PptxParser()
    elif ext == ".pdf":
        from parser.pdf_parser import PdfParser
        return PdfParser()
    else:
        from parser.mock_parser import MockParser
        return MockParser()


__all__ = ["ParserAdapter", "get_parser"]
