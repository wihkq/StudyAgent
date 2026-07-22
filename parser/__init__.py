"""Parser package - 文档解析适配器

可替换实现：MockParser / PptxParser / PdfParser
"""


class ParserAdapter:
    """文档解析抽象基类"""

    async def parse(self, file_path: str) -> list[dict]:
        """解析文档，返回 [{page, title, content}, ...]"""
        raise NotImplementedError


def get_parser(file_path: str = "") -> "ParserAdapter":
    """工厂函数：根据全局配置和文件类型返回合适的解析器

    每次调用创建新的 Settings 实例，确保环境变量变更即时生效。
    """
    from pathlib import Path

    from config.settings import Settings

    parser_mode = Settings().parser_mode

    if parser_mode == "mock":
        from parser.mock_parser import MockParser
        return MockParser()

    # live 模式：按扩展名选择解析器
    ext = Path(file_path).suffix.lower() if file_path else ""
    if ext == ".pptx":
        from parser.ppt_parser import PptxParser
        return PptxParser()
    elif ext == ".pdf":
        # PDF 解析尚未实现 (Issue-003 TODO)，降级到 Mock
        from parser.mock_parser import MockParser
        return MockParser()
    else:
        from parser.mock_parser import MockParser
        return MockParser()


__all__ = ["ParserAdapter", "get_parser"]
