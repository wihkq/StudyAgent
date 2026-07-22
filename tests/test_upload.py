"""测试：文件上传 API"""
import io

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# 最小的合法 PPTX 二进制（空压缩包）
MINIMAL_PPTX = (
    b"PK\x03\x04\x14\x00\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x0a\x00\x00\x00[Content_Types].xml"
    b"<?xml version='1.0' encoding='UTF-8'?>"
    b"<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>"
    b"<Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>"
    b"<Override PartName='/ppt/presentation.xml' "
    b"ContentType='application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'/>"
    b"</Types>"
    b"PK\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00[Content_Types].xml"
    b"PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x008\x00\x00\x00'\x01\x00\x00\x00\x00"
)


def _make_file(filename, content):
    """构造上传用的文件对象"""
    return ("file", (filename, io.BytesIO(content), "application/octet-stream"))


class TestUploadSuccess:
    """正常上传流程"""

    def test_upload_pptx_returns_201(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("计算机组成原理.pptx", MINIMAL_PPTX)],
        )
        assert response.status_code == 201
        data = response.json()
        assert data["file_id"].startswith("doc-")
        assert data["filename"] == "计算机组成原理.pptx"
        assert data["extension"] == ".pptx"
        assert data["status"] == "uploaded"
        assert data["size_mb"] > 0

    def test_upload_pdf_returns_201(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("操作系统.pdf", b"%PDF-1.4 test pdf content")],
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "操作系统.pdf"
        assert data["extension"] == ".pdf"
        assert data["status"] == "uploaded"

    def test_upload_with_course_name(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("课件.pptx", MINIMAL_PPTX)],
            data={"course_name": "计算机组成原理"},
        )
        assert response.status_code == 201
        assert response.json()["course_name"] == "计算机组成原理"

    def test_upload_without_course_name_returns_none(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("课件.pptx", MINIMAL_PPTX)],
        )
        assert response.status_code == 201
        assert response.json()["course_name"] is None

    def test_upload_file_saved_to_disk(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("test.pptx", MINIMAL_PPTX)],
        )
        data = response.json()
        from pathlib import Path
        assert Path(data["upload_path"]).exists()
        # 清理
        Path(data["upload_path"]).unlink()


class TestUploadValidation:
    """格式与大小校验"""

    def test_reject_txt_file(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("notes.txt", b"hello")],
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "UNSUPPORTED_FORMAT"

    def test_reject_no_extension(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("noext", b"data")],
        )
        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "UNSUPPORTED_FORMAT"

    def test_reject_empty_file(self):
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("empty.pptx", b"")],
        )
        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "EMPTY_FILE"

    def test_reject_oversized_file(self):
        big = b"x" * (51 * 1024 * 1024)  # 51MB
        response = client.post(
            "/api/v1/upload",
            files=[_make_file("big.pptx", big)],
        )
        assert response.status_code == 413
        assert response.json()["detail"]["error_code"] == "FILE_TOO_LARGE"

    def test_missing_file_returns_422(self):
        response = client.post("/api/v1/upload")
        assert response.status_code == 422


class TestUploadIdempotency:
    """幂等性：重复上传不冲突"""

    def test_duplicate_uploads_different_ids(self):
        resp1 = client.post(
            "/api/v1/upload",
            files=[_make_file("same.pptx", MINIMAL_PPTX)],
        )
        resp2 = client.post(
            "/api/v1/upload",
            files=[_make_file("same.pptx", MINIMAL_PPTX)],
        )
        id1 = resp1.json()["file_id"]
        id2 = resp2.json()["file_id"]
        assert id1 != id2, "每次上传应生成唯一 ID"
        # 清理
        from pathlib import Path
        Path(resp1.json()["upload_path"]).unlink()
        Path(resp2.json()["upload_path"]).unlink()
