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
    """Mock TutorAgent — 基于检索结果规则拼接，无需 LLM（Issue-016 优化版）"""

    async def answer(
        self, question: str, retrieved_chunks: list[dict]
    ) -> dict:
        if not retrieved_chunks:
            return {
                "answer": (
                    "📭 **未找到相关内容**\n\n"
                    "课程资料中暂未收录与您问题相关的知识点。\n\n"
                    "💡 建议：\n"
                    "- 检查问题是否与已上传课程相关\n"
                    "- 尝试用不同关键词提问\n"
                    "- 上传更多课程 PPT 扩充知识库"
                ),
                "sources": [],
            }

        top_chunks = retrieved_chunks[:3]
        answer_parts = []
        sources = []

        # 头部总结
        answer_parts.append(f"## 📖 {question}\n")

        for i, chunk in enumerate(top_chunks):
            meta = chunk.get("metadata", {})
            page = meta.get("page", "?")
            title = meta.get("title", "")
            content = meta.get("content", "")
            source_file = meta.get("source_file", "")
            score = chunk.get("score", 0)

            excerpt = content[:150] + ("..." if len(content) > 150 else "")

            answer_parts.append(f"### 要点 {i+1}：{title}")
            answer_parts.append(f"> {excerpt}")
            answer_parts.append(f"📄 来源：{source_file} 第 {page} 页（相关度 {score:.0%}）\n")

            sources.append({
                "page": page,
                "title": title,
                "excerpt": excerpt,
                "source_file": source_file,
                "score": round(score, 4),
            })

        # 总结
        answer_parts.append(
            f"---\n"
            f"📚 以上内容综合自课程 PPT 第 {', '.join(str(s['page']) for s in sources)} 页。\n"
            f"💡 建议：认真复习以上章节，重点理解核心概念。"
        )

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
