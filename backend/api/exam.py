"""模拟考试 API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

router = APIRouter()


class GenerateRequest(BaseModel):
    chapters: list[dict] = Field(default=[], description="课程章节列表")
    question_count: int = Field(default=5, ge=1, le=20, description="题目数量")


class GradeRequest(BaseModel):
    questions: list[dict] = Field(..., description="试卷题目列表")
    answers: list[str] = Field(..., description="学生答案列表")

    @model_validator(mode="after")
    def check_length_match(self):
        if len(self.answers) != len(self.questions):
            raise ValueError(
                f"答案数量 ({len(self.answers)}) 与题目数量 ({len(self.questions)}) 不匹配"
            )
        return self


@router.post("/exam/generate")
async def generate_exam(request: GenerateRequest) -> dict:
    """生成模拟试卷"""
    from agents.examiner_agent import get_examiner_agent

    agent = get_examiner_agent()
    return await agent.generate_exam(request.chapters, request.question_count)


@router.post("/exam/grade")
async def grade_exam(request: GradeRequest) -> dict:
    """批改试卷"""
    from agents.examiner_agent import get_examiner_agent

    agent = get_examiner_agent()
    return await agent.grade(request.questions, request.answers)
