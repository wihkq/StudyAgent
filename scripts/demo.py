#!/usr/bin/env python3
"""StudyAgent 完整演示脚本

一键跑通全流程：
  上传 → 解析 → 知识库构建 → 知识地图 → AI问答 → 复习计划 → 模拟考试

用法：
  python scripts/demo.py
"""
import asyncio
import sys
from pathlib import Path

# 确保项目根在 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.document_agent import get_document_agent
from agents.examiner_agent import get_examiner_agent
from agents.planner_agent import get_planner_agent
from agents.tutor_agent import get_tutor_agent
from knowledge.chunker import chunk_pages
from knowledge.embedding import get_embedding
from knowledge.retriever import Retriever
from knowledge.vector_store import get_vector_store


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demo():
    # Mock 数据：模拟解析后的 PPT 页面
    pages = [
        {"page": 1, "title": "课程概述", "content": "本课程介绍计算机系统的基本组成。重点掌握整体架构和核心概念。"},
        {"page": 2, "title": "数据表示", "content": "二进制是计算机的核心基础。必考数值转换方法，包括二进制与十进制互转。"},
        {"page": 3, "title": "数据表示", "content": "十六进制与二进制的转换公式。核心考点：进制转换。"},
        {"page": 4, "title": "指令系统", "content": "指令格式包括操作码和地址码。注意寻址方式：立即寻址、直接寻址、间接寻址。"},
        {"page": 5, "title": "处理器设计", "content": "数据通路和控制器是关键组件。流水线技术提高指令吞吐率。"},
        {"page": 6, "title": "存储层次", "content": "Cache、主存与虚拟存储器构成层次结构。重点：Cache 映射方式和命中率计算。"},
    ]

    async def run():
        # 1. 文档切片
        print_section("1. 文档切片")
        chunks = chunk_pages(pages, source_file="计算机组成原理.pptx")
        print(f"   共生成 {len(chunks)} 个知识 Chunk")
        for c in chunks[:3]:
            print(f"   {c['chunk_id']} | 第{c['page']}页 | {c['title']} | {c['content'][:50]}...")

        # 2. 向量化 + 入库
        print_section("2. 向量化 & 知识库构建")
        emb = get_embedding()
        store = get_vector_store(dim=128)
        retriever = Retriever(emb, store)
        ids = await retriever.add_chunks(chunks)
        print(f"   已入库 {len(ids)} 个向量")

        # 3. 知识地图
        print_section("3. 知识地图")
        doc_agent = get_document_agent()
        km = await doc_agent.analyze(pages, "计算机组成原理")
        for ch in km["chapters"]:
            stars = "⭐" * ch["importance"]
            print(f"   {stars} {ch['title']} (第{ch['pages']}页, {len(ch['key_points'])}个知识点)")

        # 4. AI 问答
        print_section("4. AI 问答")
        tutor = get_tutor_agent()
        result = await retriever.retrieve("Cache 的映射方式", top_k=3)
        answer = await tutor.answer("Cache 的映射方式", result)
        print(f"   {answer['answer']}")
        print(f"   来源: {[s['page'] for s in answer['sources']]}")

        # 5. 复习计划
        print_section("5. 复习计划")
        planner = get_planner_agent()
        plan = await planner.generate("2026-08-15", 4.0, km["chapters"])
        print(f"   {plan['summary']['message']}")
        for d in plan["plan"]:
            tasks = ", ".join(t["title"] for t in d["tasks"])
            print(f"   Day {d['day']} ({d['date']}): {tasks}")

        # 6. 模拟考试
        print_section("6. 模拟考试")
        examiner = get_examiner_agent()
        exam = await examiner.generate_exam(km["chapters"], 4)
        print(f"   生成 {len(exam['questions'])} 道题目")
        for q in exam["questions"]:
            print(f"   [{q['type']}] {q['question'][:60]}...")

        # 批改
        answers = ["A", "五个阶段：取指、译码、执行、访存、写回", "Cache 映射方式", "流水线技术"]
        grade = await examiner.grade(exam["questions"], answers)
        print(f"\n   得分: {grade['score']}/{grade['total']} ({grade['percentage']}%)")

        print_section("✅ 演示完成！")
        print("   启动 Web 界面: streamlit run frontend/app.py")
        print("   启动 API 服务: uvicorn backend.main:app --reload\n")

    asyncio.run(run())


if __name__ == "__main__":
    demo()
