"""PlannerAgent - 复习计划生成

职责：根据考试日期、可用时间、掌握程度生成个性化 Day-by-Day 复习计划。
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class PlannerAgent:
    """复习计划 Agent 抽象基类"""

    async def generate(
        self,
        exam_date: str,
        daily_hours: float,
        chapters: list[dict],
    ) -> dict:
        """生成复习计划

        Args:
            exam_date: 考试日期 (YYYY-MM-DD)
            daily_hours: 每日可用学习时间（小时）
            chapters: [{title, page_count, importance, key_points}]

        Returns:
            {plan: [{day, date, tasks: [{title, hours, type}]}], summary}
        """
        raise NotImplementedError


class MockPlannerAgent(PlannerAgent):
    """Mock PlannerAgent — 基于规则分配，无需 LLM"""

    async def generate(
        self,
        exam_date: str,
        daily_hours: float,
        chapters: list[dict],
    ) -> dict:
        if not chapters:
            return {
                "plan": [],
                "summary": {
                    "total_days": 0,
                    "message": "暂无课程章节，请先上传课程资料。",
                },
            }

        # 计算可用天数
        today = date.today()
        try:
            exam = date.fromisoformat(exam_date)
        except ValueError:
            exam = today + timedelta(days=14)

        total_days = max(1, (exam - today).days)

        # 按重要程度排序（高的先学）
        sorted_chapters = sorted(chapters, key=lambda c: c.get("importance", 1), reverse=True)

        # 分配天数：每个章节至少 1 天，重要章节额外加
        base_days = max(1, total_days // max(len(sorted_chapters), 1))
        plan = []
        current_date = today

        for ch in sorted_chapters:
            imp = ch.get("importance", 3)
            # 重要程度 4-5：2 天；2-3：1 天；1：合并到前面的复习日
            if imp >= 4 and total_days > len(sorted_chapters):
                days_for_chapter = min(2, total_days - len(plan))
            else:
                days_for_chapter = 1

            for d in range(days_for_chapter):
                if current_date > exam:
                    break
                tasks = self._daily_tasks(ch, daily_hours, d, days_for_chapter)
                plan.append({
                    "day": len(plan) + 1,
                    "date": current_date.isoformat(),
                    "tasks": tasks,
                })
                current_date += timedelta(days=1)

            if current_date > exam:
                break

        # 最后一天：总复习
        if current_date <= exam and plan:
            plan.append({
                "day": len(plan) + 1,
                "date": current_date.isoformat(),
                "tasks": [
                    {"title": "总复习与错题回顾", "hours": daily_hours, "type": "review"},
                ],
            })

        return {
            "plan": plan,
            "summary": {
                "total_days": len(plan),
                "exam_date": exam_date,
                "daily_hours": daily_hours,
                "chapters_covered": len(chapters),
                "message": f"共 {len(plan)} 天复习计划，每天 {daily_hours} 小时。",
            },
        }

    def _daily_tasks(self, chapter: dict, daily_hours: float, day_idx: int, total_days: int) -> list[dict]:
        """生成单日任务"""
        title = chapter.get("title", "")
        tasks = []

        if day_idx == 0:
            # 第一天：学习新内容
            tasks.append({"title": f"学习「{title}」核心概念", "hours": round(daily_hours * 0.5, 1), "type": "study"})
            tasks.append({"title": f"整理「{title}」笔记", "hours": round(daily_hours * 0.3, 1), "type": "note"})
            tasks.append({"title": "课后练习", "hours": round(daily_hours * 0.2, 1), "type": "practice"})
        else:
            # 第二天（仅重要章节）：复习+刷题
            tasks.append({"title": f"复习「{title}」重点", "hours": round(daily_hours * 0.4, 1), "type": "review"})
            tasks.append({"title": "真题练习", "hours": round(daily_hours * 0.6, 1), "type": "practice"})

        return tasks


def get_planner_agent() -> PlannerAgent:
    """工厂函数"""
    from config.settings import Settings

    mode = Settings().llm_mode
    if mode == "mock":
        return MockPlannerAgent()
    elif mode == "kimi":
        logger.warning("LLM_MODE=kimi，但 PlannerAgent 尚未集成 LLM，回退 Mock")
        return MockPlannerAgent()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockPlannerAgent", mode)
        return MockPlannerAgent()
