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


class LLMTutorAgent(TutorAgent):
    """真实 LLM TutorAgent — 调用 DeepSeek/Kimi API 生成回答"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def answer(self, question: str, retrieved_chunks: list[dict]) -> dict:
        if not retrieved_chunks:
            return await MockTutorAgent().answer(question, [])

        # 拼接检索内容为上下文
        context_parts = []
        sources = []
        for i, chunk in enumerate(retrieved_chunks[:5]):
            meta = chunk.get("metadata", {})
            context_parts.append(
                f"[来源{i+1} 第{meta.get('page','?')}页] {meta.get('content','')}"
            )
            sources.append({
                "page": meta.get("page", "?"),
                "title": meta.get("title", ""),
                "excerpt": meta.get("content", "")[:120],
                "source_file": meta.get("source_file", ""),
                "score": round(chunk.get("score", 0), 4),
            })

        context = "\n\n".join(context_parts)
        prompt = (
            "你是一个大学课程期末复习助手。请基于以下课程PPT内容回答学生问题。\n"
            "要求：引用具体来源页码，语言简洁有条理，帮助理解概念。\n\n"
            f"【课程内容】\n{context}\n\n"
            f"【学生问题】{question}\n\n"
            "请回答（标明来源页码）："
        )

        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": [
                        {"role": "user", "content": prompt}
                    ]},
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("LLM 调用失败: %s，回退规则回答", e)
            return await MockTutorAgent().answer(question, retrieved_chunks)

        page_str = "、".join(str(s["page"]) for s in sources)
        return {
            "answer": f"{answer}\n\n---\n📚 以上内容综合自课程 PPT 第 {page_str} 页。",
            "sources": sources,
        }


def get_tutor_agent() -> TutorAgent:
    """工厂函数"""
    from config.settings import Settings

    s = Settings()
    mode = s.llm_mode
    if mode == "mock":
        return MockTutorAgent()
    elif mode in ("kimi", "deepseek"):
        if s.llm_api_key:
            return LLMTutorAgent(
                api_key=s.llm_api_key,
                base_url=s.llm_api_base,
                model=s.llm_model,
            )
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockTutorAgent", mode)
        return MockTutorAgent()
