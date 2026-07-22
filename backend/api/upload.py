"""文件上传 API"""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

router = APIRouter()

# 允许的文件格式
ALLOWED_EXTENSIONS = {".pptx", ".pdf"}

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(..., description="课程资料文件 (.pptx / .pdf)"),
    course_name: str = Form("", description="课程名称（可选）"),
):
    """上传课程资料文件

    接收 pptx/pdf 文件，校验格式和大小后保存到本地 uploads/ 目录。
    返回文件元数据，文件内容解析由后续 Issue 实现。
    """
    # 1. 格式校验（扩展名）
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "UNSUPPORTED_FORMAT",
                "error_message": f"不支持的文件格式: {ext}，仅允许 {', '.join(ALLOWED_EXTENSIONS)}",
                "details": {"filename": file.filename, "extension": ext},
            },
        )

    # 2. 读取文件内容
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    # 3. 大小校验
    if file_size_mb == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "EMPTY_FILE",
                "error_message": "文件为空，请上传有效文件",
                "details": {"filename": file.filename},
            },
        )

    from config.settings import Settings
    max_mb = Settings().max_upload_size_mb
    if file_size_mb > max_mb:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "error_message": f"文件大小 {file_size_mb:.1f}MB 超过限制 {max_mb}MB",
                "details": {
                    "filename": file.filename,
                    "size_mb": round(file_size_mb, 1),
                    "limit_mb": max_mb,
                },
            },
        )

    # 4. Magic Bytes 校验（防止改扩展名绕过，须在大小校验之后）
    magic_signatures = {
        ".pptx": b"PK\x03\x04",
        ".pdf": b"%PDF-",
    }
    expected_magic = magic_signatures[ext]
    if not content.startswith(expected_magic):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_FILE_CONTENT",
                "error_message": f"文件内容与扩展名 {ext} 不匹配，请上传有效的 {ext} 文件",
                "details": {"filename": file.filename, "extension": ext},
            },
        )

    # 5. 保存文件（uuid 重命名，防止路径穿越）
    file_id = f"doc-{uuid.uuid4().hex[:8]}"
    safe_filename = f"{file_id}{ext}"
    save_path = UPLOAD_DIR / safe_filename

    try:
        save_path.write_bytes(content)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "SAVE_FAILED",
                "error_message": "文件保存失败",
                "details": {"filename": file.filename, "reason": str(e)},
            },
        )

    # 6. 返回元数据
    return {
        "file_id": file_id,
        "filename": file.filename,
        "size_mb": round(file_size_mb, 4),
        "course_name": course_name.strip() or None,
        "extension": ext,
        "upload_path": str(save_path),
        "status": "uploaded",
    }
