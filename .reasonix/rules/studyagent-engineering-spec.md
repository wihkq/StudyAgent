# StudyAgent 工程实施规范

你是 StudyAgent 仓库的实现工程师。一次只完成 **一个** GitHub Issue（`ISSUE-XXX`）。  
权威规格来源优先级：

1. **当前 Issue 正文**（目标 / 前置依赖 / 文件范围 / 统一命名 / 实现步骤 / 验收标准 / 测试与验证 / 降级策略）
2. 仓库根目录 `ISSUES.md` 与 `StudyAgent_技术实现.md` 中的全局约定
3. 已存在代码与测试（不得无故推翻既有契约）

Issue 写明的验收标准是 Definition of Done；未写明的功能 **不要做**。

## 项目一句话

StudyAgent = 独立部署的多 Agent 智能期末复习助手：Mock 课程资料输入 → 解析/总结/知识库构建/RAG问答/复习计划/模拟考试闭环；与具体 LLM 厂商、OCR 引擎、向量数据库 **解耦**，通过 Adapter / Provider 可替换。

## 当前阶段（极重要）

**团队现在处于 MVP 开发初期，没有真实课程资料 / 学生数据 / 考试题库。** 本阶段目标是用 Mock PPT 资料跑通 P0 核心闭环。

因此本阶段默认只做：

1. **MockPPTLoader + MockLLMProvider + Mock 课程资料** 跑通 P0 闭环与验收（上传→解析→知识库→问答→复习计划）。
2. 内部领域模型、Agent Prompt、知识库、API——全部与具体课程无关，按通用 `course/subject` 设计。
3. `ParserAdapter` / `LLMProvider` / `EmbeddingProvider` / `VectorStoreProvider` 的**接口与占位**，为以后更换模型/数据库留缝。

明确不做 / 禁止：

1. 不要连接、调用任何付费 LLM API（OpenAI/Claude 等）作为硬依赖；必须保留 Mock/本地模型降级路径。
2. 不要在 Agent Prompt 中硬编码某门具体课程的知识内容（如「计算机组成原理」）；课程知识只能来自用户上传的 PPT。
3. RAG 检索到的内容必须标注来源（PPT 页码），禁止 LLM 凭空编造知识点。
4. 不要为了「演示好看」把 Mock 数据写得像真数据一样完整；Mock 只验证流程，不冒充真实课程。
5. 验收以 Mock 资料 + 流程正确性为准；不得声称「已包含完整课程知识库」。

## 硬约束（违反即不合格）

### A. Agent 边界与 RAG 溯源

1. **LLM 生成内容必须有据可查**：Tutor Agent 的回答必须引用检索到的 PPT 页码 (`source: "page 15"`)；禁止无来源的「通用知识」冒充课程内容。
2. **知识库是唯一真相源**：Agent 回答只能基于向量数据库中检索到的 Chunk；Agent 自身 Prompt 中不得预置课程知识点。
3. **三个可替换边界**（现在用 Mock 实现，以后换真实现，不改 Agent）：
   - `ParserAdapter`：PPT/PDF 解析（Mock 或 python-pptx + PaddleOCR）
   - `LLMProvider`：大模型调用（Mock 或 OpenAI Compatible API）
   - `VectorStoreProvider`：向量存储与检索（FAISS / Milvus）
4. **Mock 必须模拟真实场景的失败路径**：空 PPT、超大文件、OCR 无文字、相似度为 0 的检索结果等；禁止 Mock 永远是「完美成功」。
5. 开发默认且本阶段唯一合格路径：`PARSER_MODE=mock` + `LLM_MODE=mock` + `VECTOR_MODE=mock_faiss`。
6. 任何 live 路径（如真实 OpenAI API）：能力默认 `UNVERIFIED`；必须有降级到 Mock 的能力，不得因网络/配额问题导致系统崩溃。

### B. 命名与结构

1. 同一概念只用一个主名；外部别名只在 Adapter 映射，不得渗入 Agent 业务层。
   - 示例：「文档解析」是主名，`python-pptx` 是实现细节，只在 ParserAdapter 内出现。
2. 目录结构（以 `StudyAgent_技术实现.md` 为准）：
   ```
   StudyAgent/
   ├── frontend/        # Streamlit/React 界面
   ├── backend/         # FastAPI 后端 + API 路由
   │   ├── api/         # 路由定义
   │   └── services/    # 业务逻辑
   ├── agents/          # Agent 定义（Prompt + 逻辑）
   ├── knowledge/       # RAG 知识库（embedding + vector_store + retriever）
   ├── parser/          # 文档解析适配器
   ├── database/        # 关系数据库模型
   ├── config/          # 配置文件
   └── tests/           # 测试
   ```
3. API 前缀 `/api/v1`；错误体 `{ error_code, error_message, details }`；分页 `{ total, page, page_size, items }`。
4. 字段命名 `snake_case`；文件名 `snake_case`。
5. **Agent 类名固定**（照抄，不重命名）：
   - `DocumentAgent` — 课程资料分析（结构提取、重点标记）
   - `TutorAgent` — 智能问答（基于 RAG 检索结果回答）
   - `PlannerAgent` — 复习计划生成
   - `ExaminerAgent` — 模拟考试与批改
6. ID 前缀格式：
   - 课程：`crs-{uuid_short}`
   - 文档/PPT：`doc-{uuid_short}`
   - 知识点 Chunk：`chk-{uuid_short}`
7. 禁止在 Agent Prompt 中硬编码演示课程名/章节名/人名；所有课程相关内容来自解析结果。

### C. 技术栈与优先级

1. **后端**：Python 3.9+ + FastAPI + Pydantic v2 + pytest。
2. **前端**：Streamlit（快速原型） → React + TypeScript + Vite（后期可选升级）。
3. **存储**：SQLite（MVP 阶段）+ FAISS（向量检索）；Milvus 为 P2 增强。
4. **LLM 一律经 `LLMProvider`**（mock / openai_compatible / local_model）；每个 Agent 必须有 **无 LLM 降级路径**（返回规则/模板化兜底）。
5. **OCR**：PaddleOCR（P1），MVP 阶段 Mock 文本替代。
6. Milvus / Neo4j / 知识图谱为 P2，不得变成 P0/P1 硬前置。
7. P1 失败不得阻断 P0；只实现本 Issue 优先级范围内的内容。

### D. 关键语义（常踩坑）

1. **Chunk ≠ 整页 PPT**：一个 Chunk 是一个独立知识点，一页 PPT 可能拆成多个 Chunk。
2. **知识库检索 ≠ 全文搜索**：RAG 用向量相似度，不是关键词匹配；检索结果为 0 时必须明确告知用户「课程资料中未找到相关内容」。
3. **Mock LLM 不等于乱编**：Mock 模式下回答必须基于传入的检索内容拼接，不能凭空生成。
4. **Agent 之间通过 API/数据层通信，不直接互相调用**：PlannerAgent 的输出是 TutorAgent 的输入上下文之一，不是代码层面的耦合。
5. **复习计划是生成结果，不是数据库状态**：Plan 由 PlannerAgent 每次根据输入重新生成，不强制持久化（MVP 阶段）。

## 执行工作流（必须按序）

### 1. 读题与范围锁定

- 完整阅读 Issue 各节，列出：
  - 交付物文件清单（以「文件范围」为准，可增测试文件，勿扩大产品范围）
  - 统一命名中的类/方法/字段/API（照抄，不改名）
  - 验收标准 checklist
  - 前置依赖：若仓库中对应能力缺失，先最小补齐 **仅使本 Issue 可验收** 的缺口，或明确阻塞并停止；不要顺手做后续 Issue。
- 若 Issue 与技术实现文档冲突：**以技术实现文档全局约定为准**，并在提交时注明冲突点。

### 2. 实现

- 严格按「实现步骤」推进；步骤未覆盖但验收需要的细节，以「统一命名」「输入上下文」补全。
- 优先复用现有模块；新增代码放在 Issue 指定路径。
- 保持小步提交，逻辑清晰；不做与本 Issue 无关的重构、文档大改、依赖升级。
- 所有依赖 LLM 的路径必须实现规则/模板降级（MockLLMProvider 或本地规则兜底）。
- 涉及 Mock：失败路径、空结果、边界情况必须覆盖，不要只写 Happy Path。

### 3. 测试与验收

- 按「测试与验证」编写/更新自动化测试；命令能跑则跑，结果贴出。
- 逐条勾验收标准；任一条不满足则继续改，不得宣称完成。
- P0 涉及 RAG 时：测试须证明检索结果包含来源页码、无来源时明确告知用户。

### 4. 交付说明

用简短结构输出：

1. **做了什么**（对应文件，附 diff 摘要）
2. **验收对照**（逐条 ✅/❌）
3. **如何跑测试**（粘贴可执行的命令）
4. **未做 / 降级**（对照 Issue「降级策略」；P2 依赖未引入则说明）
5. **风险或需人工确认项**（例如 Mock 模式下的行为与真实 LLM 的差异）

## 禁止清单

- 连接或调用未配置的付费 LLM API 并当作完成
- 在 Agent Prompt 中硬编码具体课程知识（如「Cache 的三种映射方式」）
- 扩大 Issue 范围（顺手做后续 Issue 或提前做 P2 功能）
- 用 Mock 的完美路径冒充已处理所有边界情况
- LLM 回答无来源引用（回答中必须包含 PPT 页码）
- `LLM_MODE=live` 失败时静默切 Mock 仍返回成功（必须明确告知用户降级）
- 引入方案未允许的新 Agent 名、新目录、新依赖
- 把 Milvus / Neo4j / 知识图谱做成 P0 必需
- 删除或弱化 Issue 要求的降级路径
- 在未要求时改 README / 大规模改无关文档


## 最小自检（提交前默念）

- [ ] 文件路径 ⊆ Issue「文件范围」（+ 必要测试）
- [ ] 类名/API/字段 = Issue 与全局约定的「统一命名」
- [ ] 验收标准全部可演示或可自动验证
- [ ] LLM 回答有来源引用；无来源时明确告知
- [ ] 无范围蔓延；降级策略已实现或已声明不适用
- [ ] Mock 模式覆盖了至少一个失败/边界路径
