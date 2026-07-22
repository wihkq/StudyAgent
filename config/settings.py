"""全局配置 - 每次实例化时从环境变量读取，支持运行时切换"""
import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """StudyAgent 全局配置

    所有字段通过 Field(default_factory=...) 延迟求值，
    Settings() 实例化时读取当前环境变量，
    支持同一进程中通过修改 os.environ 后创建新实例来切换配置。
    """

    # 运行模式
    parser_mode: str = Field(
        default_factory=lambda: os.getenv("PARSER_MODE", "mock")
    )  # mock | python_pptx
    llm_mode: str = Field(
        default_factory=lambda: os.getenv("LLM_MODE", "mock")
    )  # mock | openai_compatible
    vector_mode: str = Field(
        default_factory=lambda: os.getenv("VECTOR_MODE", "mock_faiss")
    )  # mock_faiss | faiss

    # 服务配置
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # 数据库
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./studyagent.db")
    )

    # LLM（Mock 模式下忽略）
    llm_api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_api_base: str = Field(
        default_factory=lambda: os.getenv(
            "LLM_API_BASE", "https://api.openai.com/v1"
        )
    )
    llm_model: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    )

    # 文件上传限制（MB）
    max_upload_size_mb: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    )


settings = Settings()
