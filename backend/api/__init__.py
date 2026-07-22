"""API 路由"""
from fastapi import APIRouter

from backend.api.chat import router as chat_router
from backend.api.plan import router as plan_router
from backend.api.upload import router as upload_router

router = APIRouter()
router.include_router(upload_router)
router.include_router(chat_router)
router.include_router(plan_router)


@router.get("/status")
async def api_status():
    """API 状态检查"""
    return {
        "api_version": "v1",
        "status": "ok",
        "available_endpoints": [
            "GET /status",
            "POST /upload",
            "POST /chat",
            "POST /plan",
        ],
    }
