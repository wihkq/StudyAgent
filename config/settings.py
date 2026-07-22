"""全局配置"""
import os
from pydantic import BaseModel


class Settings(BaseModel):
    """StudyAgent 全局配置"""

    # 运行模式
    parser_mode: str = os.getenv("PARSER_MODE", "mock")       # mock | python_pptx
    llm_mode: str = os.getenv("LLM_MODE", "mock")             # mock | openai_compatible
    vector_mode: str = os.getenv("VECTOR_MODE", "mock_faiss") # mock_faiss | faiss

    # 服务配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # 数据库
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./studyagent.db")

    # LLM（Mock 模式下忽略）
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_api_base: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    # 文件上传限制（MB）
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))


settings = Settings()
