"""StudyAgent Frontend - Streamlit 入口"""
import datetime
import random
import time
import streamlit as st

# ===== 页面配置 =====
st.set_page_config(
    page_title="StudyAgent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== 初始化 session_state =====
if "courses" not in st.session_state:
    st.session_state.courses = [
        {
            "id": "crs-demo01",
            "name": "示例课程",
            "file_count": 8,
            "chapter_count": 5,
            "upload_date": datetime.date.today().isoformat(),
            "status": "ready",  # ready / processing / error
        }
    ]
if "learning_stats" not in st.session_state:
    st.session_state.learning_stats = {
        "total_study_hours": 6.5,
        "completed_chapters": 3,
        "total_chapters": 8,
        "correct_rate": 0.78,
        "questions_answered": 24,
    }
if "exam_date" not in st.session_state:
    st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=14)


# ===== 辅助函数 =====
def add_course(name: str, file_count: int) -> None:
    """添加课程到列表（Mock）"""
    import uuid
    new_course = {
        "id": f"crs-{uuid.uuid4().hex[:6]}",
        "name": name,
        "file_count": file_count,
        "chapter_count": max(1, file_count // 2),
        "upload_date": datetime.date.today().isoformat(),
        "status": "ready",
    }
    st.session_state.courses.insert(0, new_course)


# ===== 侧边栏导航 =====
with st.sidebar:
    st.image("https://img.icons8.com/color/96/books.png", width=64)
    st.title("StudyAgent")
    st.markdown("---")
    page = st.radio(
        "导航",
        ["🏠 首页 Dashboard", "📤 上传资料", "📚 课程列表", "📊 学习进度"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    # 考试倒计时
    days_left = (st.session_state.exam_date - datetime.date.today()).days
    if days_left >= 0:
        st.metric("📅 距考试", f"{days_left} 天")
    else:
        st.error("考试日期已过")


# ===== 页面路由 =====

if page == "🏠 首页 Dashboard":
    # ---------- 首页 ----------
    st.title("📚 StudyAgent Dashboard")
    st.markdown("### 基于多模态RAG的智能期末复习助手")

    # 统计卡片行
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("课程数", len(st.session_state.courses))
    with col2:
        stats = st.session_state.learning_stats
        st.metric("已完成章节", f"{stats['completed_chapters']}/{stats['total_chapters']}")
    with col3:
        st.metric("正确率", f"{stats['correct_rate']:.0%}")
    with col4:
        st.metric("学习时长", f"{stats['total_study_hours']}h")

    st.markdown("---")

    # 考试日期设置
    col_left, col_right = st.columns([1, 2])
    with col_left:
        new_date = st.date_input("📅 设置考试日期", value=st.session_state.exam_date)
        if new_date != st.session_state.exam_date:
            st.session_state.exam_date = new_date
            st.rerun()

    # 快速入口
    st.markdown("### 🚀 功能入口")
    st.info("使用左侧导航栏切换：📤 上传资料 · 📚 课程列表 · 📊 学习进度")

    # 最近课程
    st.markdown("### 📖 最近课程")
    if st.session_state.courses:
        for c in st.session_state.courses[:3]:
            status_icon = {"ready": "✅", "processing": "⏳", "error": "❌"}
            icon = status_icon.get(c["status"], "❓")
            st.markdown(
                f"{icon} **{c['name']}** — {c['file_count']} 个文件, "
                f"{c['chapter_count']} 章节 — 上传于 {c['upload_date']}"
            )
    else:
        st.info("还没有课程，去上传资料开始吧！")


elif page == "📤 上传资料":
    # ---------- 上传页面 ----------
    st.title("📤 上传课程资料")
    st.markdown("支持 **PPT (.pptx)** 和 **PDF (.pdf)** 格式，单文件最大 50MB")

    uploaded_files = st.file_uploader(
        "拖拽或点击选择文件",
        type=["pptx", "pdf"],
        accept_multiple_files=True,
        help="支持 .pptx 和 .pdf 格式",
    )

    if uploaded_files:
        # 显示待上传文件列表
        st.markdown("### 待上传文件")
        for f in uploaded_files:
            size_mb = f.size / (1024 * 1024)
            col_f, col_s = st.columns([4, 1])
            with col_f:
                st.markdown(f"📄 **{f.name}**")
            with col_s:
                st.caption(f"{size_mb:.1f} MB")

        # 课程名输入
        course_name = st.text_input(
            "课程名称",
            value=uploaded_files[0].name.rsplit(".", 1)[0],
            placeholder="例如：高等数学",
        )

        if st.button("🚀 开始上传并解析", type="primary", use_container_width=True):
            if not course_name.strip():
                st.error("请输入课程名称")
            else:
                # Mock 上传进度
                progress_bar = st.progress(0)
                status_text = st.empty()
                steps = [
                    (0.1, "上传文件中..."),
                    (0.4, "解析 PPT 文本..."),
                    (0.6, "OCR 识别图片..."),
                    (0.8, "构建知识库..."),
                    (1.0, "完成！"),
                ]
                for pct, msg in steps:
                    time.sleep(0.3)  # Mock 延迟
                    progress_bar.progress(pct, text=msg)

                add_course(course_name, len(uploaded_files))
                st.success(f"✅ 「{course_name}」上传解析完成！")
                st.info("转到「课程列表」查看")
    else:
        # 空状态引导
        st.markdown("---")
        st.markdown("""
        ### 📋 使用说明
        1. 点击上方区域选择文件，或拖拽文件到此处
        2. 支持同时上传多个文件（同一课程）
        3. 输入课程名称后点击上传
        4. 系统会自动解析内容并构建知识库
        """)
        st.markdown("---")
        # 演示用 Mock 快速添加
        with st.expander("💡 没有 PPT？点这里添加演示课程"):
            demo_name = st.text_input("课程名称", value="示例课程", key="demo_course")
            demo_count = st.slider("模拟文件数", 1, 20, 8)
            if st.button("添加演示课程"):
                add_course(demo_name, demo_count)
                st.success(f"已添加演示课程「{demo_name}」")
                st.rerun()


elif page == "📚 课程列表":
    # ---------- 课程列表 ----------
    st.title("📚 课程列表")
    st.markdown(f"共 **{len(st.session_state.courses)}** 门课程")

    if not st.session_state.courses:
        st.info("还没有课程，去「上传资料」添加吧！")
    else:
        for course in st.session_state.courses:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    status = {"ready": "✅ 已就绪", "processing": "⏳ 解析中", "error": "❌ 失败"}
                    st.markdown(f"### {course['name']}")
                    st.caption(
                        f"{status.get(course['status'], course['status'])} · "
                        f"{course['file_count']} 个文件 · "
                        f"{course['chapter_count']} 个章节"
                    )
                with col2:
                    st.metric("文件", course["file_count"])
                with col3:
                    st.metric("章节", course["chapter_count"])
                with col4:
                    st.caption(f"上传于\n{course['upload_date']}")
                    if st.button("查看详情", key=f"detail_{course['id']}"):
                        st.info("课程详情页将在后续版本中实现")

        st.markdown("---")
        if st.button("🗑️ 清空所有课程（演示用）"):
            st.session_state.courses = []
            st.rerun()


elif page == "📊 学习进度":
    # ---------- 学习进度 ----------
    st.title("📊 学习进度")
    stats = st.session_state.learning_stats

    # 进度仪表盘
    col1, col2, col3 = st.columns(3)
    with col1:
        chapter_pct = stats["completed_chapters"] / stats["total_chapters"]
        st.metric("章节完成率", f"{chapter_pct:.0%}")
        st.progress(chapter_pct, text=f"{stats['completed_chapters']}/{stats['total_chapters']} 章")
    with col2:
        st.metric("答题正确率", f"{stats['correct_rate']:.0%}")
        st.progress(stats["correct_rate"], text=f"{stats['questions_answered']} 题已答")
    with col3:
        st.metric("累计学习", f"{stats['total_study_hours']} 小时")

    st.markdown("---")

    # 学习日历热力图（Mock 占位）
    st.markdown("### 📅 最近学习活动")
    today = datetime.date.today()
    activity_cols = st.columns(7)
    day_names = ["一", "二", "三", "四", "五", "六", "日"]
    random.seed(42)
    for i, col in enumerate(activity_cols):
        day = today - datetime.timedelta(days=6 - i)
        hours = round(random.uniform(0, 3), 1)
        with col:
            st.metric(f"周{day_names[day.weekday()]}", f"{hours}h")
            color = "🟩" if hours > 1.5 else ("🟨" if hours > 0.5 else "🟥")
            st.markdown(f"{color}" * max(1, int(hours)))

    st.markdown("---")

    # Mock 数据更新（演示用）
    with st.expander("🔧 模拟学习数据（演示用）"):
        if st.button("模拟学习 1 小时"):
            stats["total_study_hours"] += 1
            if stats["completed_chapters"] < stats["total_chapters"]:
                stats["completed_chapters"] += 1
            stats["questions_answered"] += 5
            stats["correct_rate"] = min(1.0, stats["correct_rate"] + 0.02)
            st.rerun()
        if st.button("重置学习数据"):
            st.session_state.learning_stats = {
                "total_study_hours": 0.0,
                "completed_chapters": 0,
                "total_chapters": 8,
                "correct_rate": 0.0,
                "questions_answered": 0,
            }
            st.rerun()
