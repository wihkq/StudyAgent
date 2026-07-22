"""AI 问答 API"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=20, description="检索结果数量")


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """AI 问答 — 基于课程知识库回答学生问题

    检索相关 Chunk 后由 TutorAgent 生成带来源引用的回答。
    """
    from agents.tutor_agent import get_tutor_agent
    from knowledge.embedding import get_embedding
    from knowledge.retriever import Retriever
    from knowledge.vector_store import get_vector_store

    # 构建检索器（当前阶段每次都新建，后续改为注入单例）
    embedding = get_embedding()
    vector_store = get_vector_store(dim=128)
    retriever = Retriever(embedding, vector_store)

    # 检索
    chunks = await retriever.retrieve(request.question, top_k=request.top_k)

    # 生成回答
    agent = get_tutor_agent()
    result = await agent.answer(request.question, chunks)

    return ChatResponse(answer=result["answer"], sources=result["sources"])
