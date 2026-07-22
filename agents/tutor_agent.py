"""TutorAgent - 智能问答导师

职责：基于 RAG 检索结果回答学生问题，引用 PPT 页码作为来源。
"""
import logging

logger = logging.getLogger(__name__)


class TutorAgent:
    """课程 AI 导师抽象基类"""

    async def answer(
        self, question: str, retrieved_chunks: list[dict]
    ) -> dict:
        """基于检索结果回答问题

        Args:
            question: 用户问题
            retrieved_chunks: [{id, metadata: {chunk_id, page, title, content, source_file}, score}]

        Returns:
            {answer, sources: [{page, title, excerpt}]}
        """
        raise NotImplementedError


class MockTutorAgent(TutorAgent):
    """Mock TutorAgent — 基于检索结果规则拼接，无需 LLM"""

    async def answer(
        self, question: str, retrieved_chunks: list[dict]
    ) -> dict:
        if not retrieved_chunks:
            return {
                "answer": "课程资料中未找到与您问题相关的内容。建议检查问题是否与课程相关，或上传更多课程资料。",
                "sources": [],
            }

        # 取 top-3 最相关 chunk
        top_chunks = retrieved_chunks[:3]

        # 构建回答
        answer_parts = [f"关于「{question}」："]
        sources = []

        for i, chunk in enumerate(top_chunks):
            meta = chunk.get("metadata", {})
            page = meta.get("page", "?")
            title = meta.get("title", "")
            content = meta.get("content", "")
            source_file = meta.get("source_file", "")

            # 截取关键词句
            excerpt = content[:120] + ("..." if len(content) > 120 else "")

            answer_parts.append(f"{i+1}. {excerpt}")
            sources.append({
                "page": page,
                "title": title,
                "excerpt": excerpt,
                "source_file": source_file,
            })

        answer_parts.append(f"\n以上内容来自课程 PPT 第 {', '.join(str(s['page']) for s in sources)} 页。")
        return {
            "answer": "\n".join(answer_parts),
            "sources": sources,
        }


def get_tutor_agent() -> TutorAgent:
    """工厂函数"""
    from config.settings import Settings

    mode = Settings().llm_mode
    if mode == "mock":
        return MockTutorAgent()
    elif mode == "kimi":
        logger.warning("LLM_MODE=kimi，但 TutorAgent 尚未集成 LLM，回退 Mock")
        return MockTutorAgent()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockTutorAgent", mode)
        return MockTutorAgent()
