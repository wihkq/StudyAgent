"""PPT 解析器 — 基于 python-pptx 的真实实现"""
from pathlib import Path

from pptx import Presentation

from parser import ParserAdapter


class PptxParser(ParserAdapter):
    """PPTX 文档解析器

    使用 python-pptx 提取每页幻灯片的标题和正文文本。
    """

    def _extract_title(self, slide) -> str:
        """从 slide 中提取标题文本"""
        # 优先取 title placeholder
        if slide.shapes.title and slide.shapes.title.text.strip():
            return slide.shapes.title.text.strip()

        # 退而求其次：取第一个有文本的 shape 作为标题
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text.strip():
                text = shape.text.strip()
                # 用第一行作为标题
                return text.split("\n")[0][:100]
        return ""

    def _extract_content(self, slide) -> str:
        """从 slide 中提取正文文本（排除标题）"""
        texts = []
        title_text = self._extract_title(slide)

        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text and text != title_text:
                        texts.append(text)

        return "\n".join(texts)

    async def parse(self, file_path: str) -> list[dict]:
        """解析 PPTX 文件

        Args:
            file_path: PPTX 文件路径

        Returns:
            [{page, title, content}, ...] 每页一个元素

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不是有效的 PPTX 格式
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() != ".pptx":
            raise ValueError(f"不支持的文件格式: {path.suffix}，需要 .pptx")

        prs = Presentation(str(path))
        pages = []

        for i, slide in enumerate(prs.slides):
            title = self._extract_title(slide)
            content = self._extract_content(slide)
            pages.append({
                "page": i + 1,
                "title": title,
                "content": content,
            })

        return pages
