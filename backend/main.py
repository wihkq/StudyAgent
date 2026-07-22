"""StudyAgent Backend - FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import router as api_router
from config.settings import settings

app = FastAPI(
    title="StudyAgent",
    description="基于多模态RAG的智能期末复习助手",
    version="0.1.0",
)

# CORS（开发阶段允许所有来源，生产需收紧）
# TODO: 生产环境替换 allow_origins 为具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径 - 服务健康检查"""
    return {
        "service": "StudyAgent",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}
