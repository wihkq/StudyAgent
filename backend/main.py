"""StudyAgent Backend - FastAPI 应用入口"""
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import router as api_router

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

# 统一校验错误格式为 {error_code, error_message, details}
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """将 Pydantic 422 转为与业务错误一致的格式"""
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "error_message": "请求参数校验失败",
            "details": [
                {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
                for e in errors
            ],
        },
    )

app.add_exception_handler(RequestValidationError, validation_exception_handler)

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
