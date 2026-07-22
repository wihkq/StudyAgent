"""复习计划 API"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class PlanRequest(BaseModel):
    exam_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="考试日期 YYYY-MM-DD")
    daily_hours: float = Field(default=4.0, ge=0.5, le=16.0, description="每日学习小时数")
    chapters: list[dict] = Field(default=[], description="课程章节列表")


@router.post("/plan")
async def create_plan(request: PlanRequest) -> dict:
    """生成个性化复习计划"""
    from agents.planner_agent import get_planner_agent

    agent = get_planner_agent()
    result = await agent.generate(
        exam_date=request.exam_date,
        daily_hours=request.daily_hours,
        chapters=request.chapters,
    )
    return result
