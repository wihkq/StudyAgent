"""StudyAgent Frontend - Streamlit 入口"""
import streamlit as st

st.set_page_config(
    page_title="StudyAgent",
    page_icon="📚",
    layout="wide",
)

st.title("📚 StudyAgent")
st.markdown("### 基于多模态RAG的智能期末复习助手")

# 侧边栏
with st.sidebar:
    st.header("导航")
    page = st.radio(
        "选择功能",
        ["🏠 首页", "📤 上传资料", "💬 AI问答", "📅 复习计划", "📊 学习进度"],
    )

if page == "🏠 首页":
    st.info("欢迎使用 StudyAgent！请从侧边栏选择功能。")
    st.markdown("""
    ### 🚀 快速开始
    1. **上传资料** — 上传课程 PPT 或 PDF
    2. **AI问答** — 基于课程内容提问
    3. **复习计划** — 自动生成学习计划
    4. **学习进度** — 追踪你的复习进度
    """)
elif page == "📤 上传资料":
    st.info("上传功能将在 Issue-003 中实现")
elif page == "💬 AI问答":
    st.info("问答功能将在 Issue-010 中实现")
elif page == "📅 复习计划":
    st.info("复习计划功能将在 Issue-011 中实现")
elif page == "📊 学习进度":
    st.info("学习进度功能将在 Issue-014 中实现")
