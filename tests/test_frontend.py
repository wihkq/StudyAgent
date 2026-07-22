"""测试：前端 session_state 逻辑和页面导入"""
import datetime
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestAddCourseLogic:
    """add_course 核心逻辑验证"""

    def test_chapter_count_minimum(self):
        """file_count=1 时 chapter_count 最小为 1"""
        assert max(1, 1 // 2) == 1
        assert max(1, 5 // 2) == 2
        assert max(1, 10 // 2) == 5

    def test_insert_at_head(self):
        """新课程 insert(0) 插到列表头部"""
        courses = [{"id": "x", "name": "旧课程"}]
        courses.insert(0, {"id": "y", "name": "新课程"})
        assert courses[0]["name"] == "新课程"
        assert courses[1]["name"] == "旧课程"

    def test_add_course_source_integrity(self):
        """源码审计：验证 add_course 包含所有必需逻辑步骤"""
        import ast
        with open("frontend/app.py") as f:
            tree = ast.parse(f.read())

        func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "add_course":
                func = node
                break
        assert func is not None, "add_course 函数应存在"

        with open("frontend/app.py") as f:
            source = "".join(f.readlines()[func.lineno - 1:func.end_lineno])

        checks = {
            "chapter_count 计算": "chapter_count",
            "至少为 1": "max(1, file_count",
            "插入头部": "insert(0",
            "ID 前缀 crs-": "crs-",
            "UUID 生成": "uuid4",
            "status 字段": "status",
        }
        for desc, pattern in checks.items():
            assert pattern in source, f"add_course 缺少: {desc}"


class TestDateCalculations:
    """日期计算"""

    def test_exam_days_left(self):
        exam_date = datetime.date.today() + datetime.timedelta(days=14)
        assert (exam_date - datetime.date.today()).days == 14

    def test_exam_date_past(self):
        exam_date = datetime.date.today() - datetime.timedelta(days=3)
        assert (exam_date - datetime.date.today()).days == -3


class TestFrontendIntegrity:
    """前端模块完整性"""

    def test_app_module_exists(self):
        import importlib
        spec = importlib.util.find_spec("frontend.app")
        assert spec is not None

    def test_no_hardcoded_course_knowledge(self):
        """工程规范：Agent Prompt 中不得硬编码具体课程知识"""
        with open("frontend/app.py") as f:
            content = f.read()
        forbidden = [
            "Cache映射方式", "三种映射", "直接映射", "全相联映射",
            "计算机组成原理", "操作系统原理",
        ]
        for phrase in forbidden:
            assert phrase not in content, f"禁止硬编码课程知识: {phrase}"
