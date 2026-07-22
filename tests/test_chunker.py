"""测试：文档切片模块"""
from knowledge.chunker import chunk_pages


class TestChunkerBasics:
    """基本切分行为"""

    def test_empty_pages_returns_empty(self):
        result = chunk_pages([], source_file="test.pptx")
        assert result == []

    def test_single_page_single_paragraph(self):
        pages = [{"page": 1, "title": "概述", "content": "这是一段测试内容。"}]
        result = chunk_pages(pages, source_file="test.pptx")
        assert len(result) == 1
        assert result[0]["chunk_id"].startswith("chk-")
        assert result[0]["page"] == 1
        assert result[0]["title"] == "概述"
        assert result[0]["content"] == "这是一段测试内容。"
        assert result[0]["source_file"] == "test.pptx"

    def test_short_paragraphs_merged(self):
        """短于 min_size 的多个段落合并为一个 chunk"""
        pages = [{
            "page": 1, "title": "Cache",
            "content": "短句A。\n\n短句B。\n\n短句C。"
        }]
        result = chunk_pages(pages, source_file="test.pptx")
        # 三个短句都 < 50 字符，合并为 1 个 chunk
        assert len(result) == 1
        assert "短句A" in result[0]["content"]
        assert "短句C" in result[0]["content"]

    def test_all_chunks_share_page_metadata(self):
        pages = [{
            "page": 5, "title": "存储层次",
            "content": "A" * 60 + "\n\n" + "B" * 60 + "\n\n" + "C" * 60
        }]
        result = chunk_pages(pages, source_file="course.pptx")
        assert len(result) == 3
        for c in result:
            assert c["page"] == 5
            assert c["title"] == "存储层次"
            assert c["source_file"] == "course.pptx"


class TestChunkerEdgeCases:
    """边界条件"""

    def test_page_without_content_uses_title(self):
        pages = [{"page": 1, "title": "章节标题", "content": ""}]
        result = chunk_pages(pages)
        assert len(result) == 1
        assert result[0]["content"] == "章节标题"

    def test_page_with_empty_both(self):
        pages = [{"page": 1, "title": "", "content": ""}]
        result = chunk_pages(pages)
        assert result == []

    def test_short_paragraph_merged(self):
        """短于 min_size 的段落合并到前一个 chunk"""
        pages = [{
            "page": 1, "title": "T",
            "content": "ABCDEFGHIJ" * 10 + "\n\n短"
        }]
        result = chunk_pages(pages, min_size=50)
        # "短" 只有 1 个字符，应合并到前面的长段落
        assert len(result) == 1
        assert "短" in result[0]["content"]

    def test_single_line_splits_by_newline(self):
        pages = [{"page": 1, "title": "T", "content": "A"*60 + "\n" + "B"*60 + "\n" + "C"*60}]
        result = chunk_pages(pages)
        assert len(result) == 3

    def test_unique_chunk_ids(self):
        pages = [{"page": 1, "title": "T", "content": "A\n\nB\n\nC"}]
        result = chunk_pages(pages)
        ids = [c["chunk_id"] for c in result]
        assert len(set(ids)) == len(ids), "所有 chunk_id 应唯一"

    def test_missing_optional_fields_default(self):
        """page_info 缺少 title 字段时使用空字符串"""
        pages = [{"page": 1, "content": "内容"}]
        result = chunk_pages(pages)
        assert result[0]["title"] == ""
