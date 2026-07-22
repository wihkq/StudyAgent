"""ParserAdapter - PPT 解析接口"""
# TODO: Issue-004 实现


class ParserAdapter:
    """文档解析抽象基类"""

    async def parse(self, file_path: str) -> list[dict]:
        """解析文档，返回 [{page, title, content}, ...]"""
        raise NotImplementedError
