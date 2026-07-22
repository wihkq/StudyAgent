"""文档切片模块 — 将解析后的 PPT 文本切分为可检索的知识 Chunk"""
import re
import uuid

# 最小/目标 Chunk 长度（字符）
MIN_CHUNK_SIZE = 50
TARGET_CHUNK_SIZE = 500


def chunk_pages(
    pages: list[dict],
    source_file: str = "",
    min_size: int = MIN_CHUNK_SIZE,
) -> list[dict]:
    """将解析后的 PPT 页面内容切分为知识 Chunk

    Args:
        pages: [{page, title, content}, ...] 来自 ParserAdapter.parse()
        source_file: 原始文件名
        min_size: 小于此长度的 chunk 合并到前一个

    Returns:
        [{chunk_id, page, title, content, source_file}, ...]
    """
    chunks = []

    for page_info in pages:
        page_num = page_info["page"]
        title = page_info.get("title", "")
        content = page_info.get("content", "")

        if not content.strip():
            # 空页面：title 本身作为一个 chunk
            if title.strip():
                chunks.append(_make_chunk(page_num, title, title, source_file))
            continue

        # 按段落切分（双换行优先，单换行其次，句号分割兜底）
        paragraphs = _split_content(content)

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 检查是否应该合并到前一个 chunk
            if chunks and len(para) < min_size:
                prev = chunks[-1]
                prev["content"] = f"{prev['content']}\n{para}"
            else:
                chunks.append(_make_chunk(page_num, title, para, source_file))

    return chunks


def _split_content(content: str) -> list[str]:
    """将文本切分为段落"""
    # 先按双换行切
    if "\n\n" in content:
        parts = content.split("\n\n")
    elif "\n" in content:
        parts = content.split("\n")
    else:
        # 按句号分割长文本
        parts = re.split(r"(?<=[。！？])", content)

    return [p.strip() for p in parts if p.strip()]


def _make_chunk(page: int, title: str, content: str, source_file: str) -> dict:
    """创建标准 Chunk 结构"""
    return {
        "chunk_id": f"chk-{uuid.uuid4().hex[:8]}",
        "page": page,
        "title": title,
        "content": content,
        "source_file": source_file,
    }
