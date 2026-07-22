"""ExaminerAgent - 模拟考试与批改

职责：基于课程知识库自动生成模拟题并评分。
"""
import logging
import random

logger = logging.getLogger(__name__)


class ExaminerAgent:
    """模拟考试 Agent 抽象基类"""

    async def generate_exam(self, chapters: list[dict], question_count: int = 5) -> dict:
        """生成模拟试卷"""
        raise NotImplementedError

    async def grade(self, questions: list[dict], answers: list[str]) -> dict:
        """批改试卷"""
        raise NotImplementedError


class MockExaminerAgent(ExaminerAgent):
    """Mock ExaminerAgent — 基于规则生成题目和评分，无需 LLM"""

    async def generate_exam(self, chapters: list[dict], question_count: int = 5) -> dict:
        if not chapters:
            return {"questions": [], "message": "暂无课程内容，无法生成试卷。"}

        all_points = []
        for ch in chapters:
            for kp in ch.get("key_points", []):
                if kp.strip():
                    all_points.append({"point": kp, "title": ch.get("title", "")})

        if not all_points:
            return {"questions": [], "message": "课程中暂无知识点，无法生成试卷。"}

        # 随机选 N 个知识点生成题目
        selected = random.sample(all_points, min(question_count, len(all_points)))
        questions = []

        for i, item in enumerate(selected):
            if i % 2 == 0:
                # 选择题
                q = self._make_choice(item)
            else:
                # 简答题
                q = self._make_short_answer(item)
            questions.append(q)

        return {
            "questions": questions,
            "total": len(questions),
            "message": f"已生成 {len(questions)} 道题目。",
        }

    async def grade(self, questions: list[dict], answers: list[str]) -> dict:
        if len(answers) != len(questions):
            raise ValueError(
                f"答案数量 ({len(answers)}) 与题目数量 ({len(questions)}) 不匹配"
            )
        results = []
        correct = 0

        for q, ans in zip(questions, answers):
            if q["type"] == "choice":
                is_correct = (ans.strip().upper() == q["answer"].strip().upper())
            else:
                # 简答题：关键词匹配
                keywords = q.get("keywords", [])
                is_correct = any(kw in ans for kw in keywords) if keywords else bool(ans.strip())

            results.append({
                "question": q["question"],
                "your_answer": ans,
                "correct_answer": q["answer"],
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
            })
            if is_correct:
                correct += 1

        return {
            "results": results,
            "score": correct,
            "total": len(questions),
            "percentage": round(correct / max(len(questions), 1) * 100, 1),
            "message": f"得分 {correct}/{len(questions)}（{correct / max(len(questions), 1) * 100:.0f}%）",
        }

    def _make_choice(self, item: dict) -> dict:
        """生成选择题"""
        point = item["point"]
        # 用知识点前半部分作题干
        parts = point.split("。")[0].split("，")[0].strip()
        question_text = f"关于「{item['title']}」，以下哪项描述正确？"

        return {
            "type": "choice",
            "question": question_text,
            "options": [
                f"A. {parts}",
                "B. 与该知识点无关的描述",
                "C. 以上都不对",
                "D. 以上都对",
            ],
            "answer": "A",
            "explanation": f"正确选项：{parts}",
            "keywords": [],
        }

    def _make_short_answer(self, item: dict) -> dict:
        """生成简答题"""
        point = item["point"]
        keywords = [w for w in point.replace("、", "，").split("，") if len(w) > 1][:3]

        return {
            "type": "short_answer",
            "question": f"请简述「{item['title']}」中的：{point[:50]}...",
            "answer": point,
            "keywords": keywords,
            "explanation": f"参考：{point}",
        }


def get_examiner_agent() -> ExaminerAgent:
    """工厂函数"""
    from config.settings import Settings

    mode = Settings().llm_mode
    if mode == "mock":
        return MockExaminerAgent()
    elif mode == "kimi":
        logger.warning("LLM_MODE=kimi，但 ExaminerAgent 尚未集成 LLM，回退 Mock")
        return MockExaminerAgent()
    else:
        logger.warning("未知 LLM_MODE=%s，回退 MockExaminerAgent", mode)
        return MockExaminerAgent()
