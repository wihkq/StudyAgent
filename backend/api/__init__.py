"""API 路由"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def api_status():
    """API 状态检查"""
    return {
        "api_version": "v1",
        "status": "ok",
        "available_endpoints": [
            "GET /status",
        ],
    }
