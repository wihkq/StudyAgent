"""PDF 解析器 — 占位（Issue-003 TODO，当前 PDF 解析由 MockParser 处理）"""
# TODO: Issue-003 实现真实 PDF 解析

from parser import ParserAdapter


class PdfParser(ParserAdapter):
    """PDF 文档解析实现"""
    pass


__all__ = ["PdfParser"]
