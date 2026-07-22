# 📚 StudyAgent

基于 LLM + RAG + Agent 的智能期末复习助手。

## 项目简介

StudyAgent 帮助学生将课程 PPT/PDF 快速转化为：
- 结构化笔记与知识地图
- 基于课程内容的智能问答
- 个性化复习计划
- 模拟考试与错题分析

## 技术栈

| 层 | 技术 |
|-----|------|
| 前端 | Streamlit（MVP）/ React（后期） |
| 后端 | Python 3.11 + FastAPI |
| AI | LangChain / LlamaIndex + Agent |
| 向量库 | FAISS（MVP）/ Milvus（后期） |
| 数据库 | SQLite（MVP） |

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端
uvicorn backend.main:app --reload --port 8000

# 4. 新终端，启动前端
streamlit run frontend/app.py
```

访问：
- 后端 API 文档：http://localhost:8000/docs
- 前端界面：http://localhost:8501

## 项目结构

```
StudyAgent/
├── frontend/        # Streamlit Web 界面
├── backend/         # FastAPI 后端
│   ├── api/         # API 路由
│   └── services/    # 业务逻辑
├── agents/          # AI Agent 定义
│   ├── document_agent.py   # 课程资料分析
│   ├── tutor_agent.py      # 智能问答
│   ├── planner_agent.py    # 复习计划
│   └── examiner_agent.py   # 模拟考试
├── knowledge/       # RAG 知识库
│   ├── embedding.py        # 向量化接口
│   ├── vector_store.py     # 向量存储接口
│   └── retriever.py        # 检索接口
├── parser/          # 文档解析适配器
├── database/        # 数据库模型
├── config/          # 全局配置
└── tests/           # 测试
```

## 运行模式

通过环境变量控制：

```bash
# Mock 模式（默认，无需外部依赖）
PARSER_MODE=mock LLM_MODE=mock VECTOR_MODE=mock_faiss

# Live 模式（需配置 API Key）
LLM_MODE=openai_compatible LLM_API_KEY=sk-xxx
```

## 开发路线

详见 [ISSUES.md](ISSUES.md) — 18 个 Issue，6 个 Phase。

## License

MIT
