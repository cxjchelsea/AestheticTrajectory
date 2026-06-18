# V4-D：Agent Runtime & MCP Integration

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-18
```

## 1. 本轮目标

在 V4-A runtime、V4-B 时间轴、V4-C 知识图谱之上，建立 **evidence-bound 审美观察 Agent** 与 **MCP 分层接入**：

```text
用户显式触发观察任务
↓
Agent 规划（reason）+ 调用内部只读工具（report / timeline / profile / knowledge）
↓
生成观察摘要 + 观察问题（每条绑定 evidenceRefs）
↓
agent_action_logs 持久化（toolName / inputRefs / outputRefs / reason）
↓
（可选）本地 MCP server 暴露同一套 internal tools
↓
（可选）用户确认的外部上下文导入批次 → external_context（supplementary only）
```

本轮完成后，用户应能：

- 在 Profile 或 Timeline 页 **主动触发** 一次观察摘要，看到基于已有 report / timeline / profile 的聚合说明（非诊断）。
- 展开摘要中的 evidenceRefs，追溯到具体 report / insight / timeline event。
- 在 Debug / Agent 审计 API 查看每次 tool call 的 reason 与 input/output refs。
- 确认 Agent 输出与 MCP 导入内容 **不进入** profile positive evidence（V3 治理仍成立）。
- （可选）通过本地 MCP server 以标准协议调用 internal read-only tools。

## 2. 上游版本决策

引用 `docs/iterations/v4-0-long-term-personalized-agent-research.md` §7.5、§7.6、§9.3、§9.5、§V4-D：

- V4-D 在 V4-C 之后、V4-E 之前。
- Agent 第一版是 **观察摘要 + 工具调用**，不是无边界自主 Agent。
- MCP **先 internal tools**，再接 **用户确认的外部只读导入**。
- Agent plan / action 必须持久化 reason、toolName、inputRefs、outputRefs。
- Agent **不得**绕过 feedback governance 直接改 profile 正向证据。
- MCP / 外部内容标记为 `external_context`，不是 preference fact。

引用 `docs/19-记忆与用户模型设计文档.md` §10.3–10.4：

- Agent 读取 L1–L5；写入 L3 只能走受 governance 约束的工具（V4-D 默认 **只读** 工具集）。
- MCP 导入需 user-confirmed；默认 supplementary context。

引用 V4-B / V4-C 已落地边界：

- Timeline / knowledge 仍为 supplementary；Agent 只能 **引用** 已有 evidence，不能发明新偏好。
- 周期摘要（V4-B）为规则聚合；Agent 摘要为其上的 **可选 LLM 编排层**，必须 cite refs。

## 3. 本轮解决什么问题

本轮解决：

```text
如何在固定 workflow 与 memory governance 不被破坏的前提下，引入可审计的 Agent 工具编排与 MCP 分层接入？
```

本轮不解决：

- 复杂 Agent 聊天壳、多轮对话记忆、自主定时任务（V4-D 仅用户触发）。
- 生产级第三方 OAuth MCP（Notion / Instapaper / Pinterest 等）——首版可用 **mock external batch + 确认流** 验证治理。
- Agent 自动更新 profile / timeline / 知识图谱。
- V4-E 的 grouping stability、failure replay 全链路（留 V4-E）。
- 真实 vision/audio LLM 解析（仍属 V4-A mock/heuristic 边界）。

## 4. 当前实现快照（V4-D 起点）

| 能力 | 当前状态 |
| --- | --- |
| 固定 workflow | `aesthetic_analysis_v1` 完整 pipeline（含 trajectory、knowledge graph） |
| 内部 API | inputs / reports / profiles / timeline / aesthetic-knowledge / analysis_jobs |
| Agent runtime | **无**；debug 中 `Agent / MCP runtime` 为 `planned` |
| agent_action_logs | v4-0 候选表；**无** migration / model |
| observation summary | V4-B `timeline/summary` 为规则聚合；**无** Agent 编排层 |
| MCP server | **无** |
| external import | **无** import batch / external_context 模型 |
| 前端 | 无 Agent 触发 UI、无 MCP 连接 UI |

## 5. 外部调研与方案选择

调研层级：

```text
版本级：引用 v4-0 §7.5–7.6、§9.3、§9.5
能力级：evidence-bound agent vs chat agent、internal MCP vs external OAuth
实现级：in-process tools vs stdio MCP、mock external batch vs 真 OAuth
```

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| Agent 交互形态 | **用户触发观察任务** + 单次摘要/问题输出；不做常驻 chat |
| 工具范围（首版） | **只读 internal tools**：reports、timeline、profile、knowledge graph |
| LLM 角色 | **规划 + 摘要生成**；工具执行走确定性 Python service，不经 LLM 伪造结果 |
| MCP 首版范围 | **本地 stdio MCP server** 暴露与 Agent 相同的 internal tools；OAuth 外部源用 mock batch 验证治理 |
| 外部导入 | **用户确认 import batch** → `external_context_items`；标记 supplementary |
| 与 workflow 关系 | Agent **不替换** `aesthetic_analysis_v1`；可 **可选调用** `create_job` 工具（dev_only 边界） |
| 审计 | `agent_action_logs` 表 + debug trace 扩展 |

### 5.2 外部调研记录

#### 记录 1：PersonaAgent — episodic + semantic memory 协同

来源名称：PersonaAgent: Bridging Memory and Action for Personalized LLM Agents

来源类型：论文

链接或出处：`https://arxiv.org/abs/2407.03181`（v4-0 §6.2 引用）

调研问题：

- Agent 如何避免平行黑盒 persona？

核心做法：

- 分离 episodic 与 semantic memory；action 必须 grounded in retrieved facts。

对 V4-D 的启发：

- Agent 读取已有 profile / timeline / reports（L1–L5），不另建 hidden persona store。

采用结论：

```text
Agent 编排层复用 V2/V3/V4 已持久化事实；action log 可回放。
```

#### 记录 2：MCP Authorization OAuth 2.1

来源名称：Model Context Protocol Authorization Specification

来源类型：官方规范

链接或出处：`https://modelcontextprotocol.io/docs/tutorials/security/authorization`

调研问题：

- 远程 MCP 最低安全要求是什么？

核心做法：

- OAuth 2.1 + PKCE；resource server 校验 token audience/scope；用户 consent。

对 V4-D 的启发：

- V4-D **首版**用 local stdio MCP（无 OAuth）暴露 internal tools。
- 外部源用 **in-app 确认 import batch** 模拟 MCP 治理，V4-D+ 再接 OAuth。

采用结论：

```text
internal MCP 先行（stdio）；external OAuth 不阻塞 V4-D MVP。
```

#### 记录 3：ReAct / tool-use 可审计模式

来源名称：ReAct: Synergizing Reasoning and Acting in Language Models

来源类型：论文 / 工程实践

链接或出处：`https://arxiv.org/abs/2210.03629`

调研问题：

- 如何让 tool call 可解释？

核心做法：

- 交错 reasoning trace 与 action；每步 action 有明确输入。

对 V4-D 的启发：

- 持久化 `reason` + `toolName` + `inputRefs` + `outputRefs`；UI/debug 可展开。

采用结论：

```text
Observation session = 有限步数 ReAct loop（max 5 tools），超限则 abstain。
```

#### 记录 4：v4-0 内部工具 MCP 优先

来源名称：项目版本级决策

来源类型：v4-0 §9.3

调研问题：

- MCP 应先接什么？

核心做法：

- 先 `retrieve report / list history / get profile` 等 internal tools，再接外部收藏源。

对 V4-D 的启发：

- MCP server tool 列表与 Agent in-process registry **同源**，避免两套契约。

采用结论：

```text
Shared ToolRegistry；Agent 与 MCP 共用 schema 与 governance tests。
```

### 5.3 方案对比

#### Agent 运行时

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 纯 prompt 摘要（无 tools） | 简单 | 不可审计、易幻觉 | 拒绝 |
| B 有限步 tool loop + action log | 可审计、复用现有 API | 需 LLM runtime | **采用** |
| C 全自主 multi-agent | 能力强 | 超 V4-D、治理难 | 拒绝 |

#### MCP 接入

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 仅 in-process tools | 最快落地 | 无 MCP 标准验证 | 作为 Agent 内核 |
| B stdio MCP + internal tools | 标准协议、可 Inspector 调试 | 需额外进程 | **V4-D 可选采用** |
| C 远程 OAuth MCP + 外部 SaaS | 真实集成 | OAuth/scope 工程量大 | 推迟到 V4-D+ / V5 |

#### 外部上下文

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A mock import batch API | 可测治理、无 OAuth | 非真实数据源 | **V4-D 采用** |
| B 真实 MCP external server | 真实 | 授权复杂 | 推迟 |
| C 静默 background sync | 体验好 | 违反 v4-0 治理 | 拒绝 |

## 6. 系统边界

### 6.1 必做

- [x] Schema + migration：`agent_action_logs`、`observation_sessions`、`external_import_batches`、`external_context_items`。
- [x] `AgentToolRegistry`：只读 internal tools（reports / timeline / profile / knowledge）。
- [x] `ObservationAgentService`：用户触发 → plan → execute tools → summary + questions。
- [x] 持久化 action log；每条 summary/question 含 `evidenceRefs` + disclaimer。
- [x] API：`POST /api/users/{id}/observations`（触发）、`GET .../observations/{id}`、`GET .../agent-actions`。
- [x] Mock external import：`POST .../external-imports` + `POST .../external-imports/{id}/confirm`（用户确认）。
- [ ] Debug trace：Agent step、tool calls、abstention、external context 路径（workflow debug 仍 planned；观察 API 自带 agent-actions 审计）。
- [x] 前端：Profile 页「生成观察摘要」入口 + 结果/evidence 展开。
- [x] Governance 测试：Agent / external context 不 feed profile positive evidence。
- [ ] 上升 `07` / `11` / `19` §10.3–10.4；`15` 记录。

### 6.2 可选（V4-D stretch）

- [x] 本地 `stdio` MCP server（`backend/mcp/internal_tools_server.py`）暴露 tool catalog。
- [ ] Ollama LLM 规划（`AGENT_RUNTIME=ollama`）；测试默认 `mock` planner。
- [x] 观察问题 UI（1–3 条非诊断式追问）。

### 6.3 不做

- [ ] 无边界自主 scheduling / push 通知。
- [ ] Agent 直接写 profile / timeline / knowledge graph。
- [ ] 生产级第三方 OAuth MCP。
- [ ] 复杂聊天壳、多 session 记忆。
- [ ] 把 external / agent 文本写入 insight `evidenceRefs` 替代当前输入。

## 7. 架构影响

### 7.1 数据模型（拟采用）

```text
agent_action_logs
  id, user_id, session_id, step_index, tool_name, reason, input_refs_json,
  output_refs_json, status, latency_ms, created_at

observation_sessions
  id, user_id, status, trigger_source, summary, questions_json, evidence_refs_json,
  disclaimer, created_at, finished_at

external_import_batches
  id, user_id, source_system, status (pending_confirmation|confirmed|rejected),
  item_count, confirmed_at, created_at

external_context_items
  id, batch_id, user_id, title, snippet, source_uri, tags_json, created_at
```

Chroma / 向量：V4-D **不新增** collection；external context 首版 tag/metadata 检索即可。

### 7.2 Internal Tool 列表（拟）

| toolName | 说明 | 读写 |
| --- | --- | --- |
| `list_reports` | 用户报告摘要列表 | 只读 |
| `get_report` | 单报告详情 | 只读 |
| `get_timeline_summary` | 周/月轨迹摘要 | 只读 |
| `list_timeline_events` | 时间轴事件 | 只读 |
| `get_profile` | 当前 profile | 只读 |
| `get_knowledge_graph` | 1-hop 概念子图 | 只读 |
| `list_knowledge_chunks` | 知识 chunk 列表 | 只读 |

可选 dev_only：

| `create_analysis_job` | 触发分析 | 写；需显式边界警告 |

### 7.3 API 设计（拟）

| 路径 | 方法 | 说明 |
| --- | --- | --- |
| `/api/users/{user_id}/observations` | POST | 用户触发观察 session |
| `/api/users/{user_id}/observations/{session_id}` | GET | 摘要 + questions + evidenceRefs |
| `/api/users/{user_id}/agent-actions` | GET | 审计 log（可按 session 过滤） |
| `/api/users/{user_id}/external-imports` | POST | 创建待确认 import batch（mock/metadata） |
| `/api/users/{user_id}/external-imports/{batch_id}/confirm` | POST | 用户确认导入 |
| `/api/users/{user_id}/external-imports/{batch_id}/reject` | POST | 用户拒绝 |

### 7.4 模块与目录（拟）

```text
backend/app/schemas/agent.py
backend/app/schemas/external_context.py
backend/app/models/persistence.py          # AgentActionLogModel, ...
backend/app/repositories/agent_action_repository.py
backend/app/repositories/external_import_repository.py
backend/app/agent/tool_registry.py
backend/app/agent/tools/                   # 各 internal tool handler
backend/app/agent/observation_agent.py     # plan + execute loop
backend/app/services/observation_service.py
backend/app/api/routes/observations.py
backend/app/api/routes/external_imports.py
backend/mcp/internal_tools_server.py       # 可选 stdio MCP
frontend/src/services/observationApi.ts
frontend/src/pages/ProfilePage.tsx         # 或 TimelinePage 增加入口
```

### 7.5 Agent 执行流程（拟）

```text
POST /observations { triggerSource, period? }
→ load user context bounds (max reports, max tools)
→ planner (mock | ollama) selects next tool + reason
→ execute tool via ToolRegistry (deterministic service calls)
→ log agent_action
→ repeat until summary ready OR max_steps OR abstain
→ persist observation_session
→ return summary + questions + evidenceRefs + disclaimer
```

### 7.6 治理不变量

1. Agent summary/question 每条必须有 ≥1 evidenceRef 指向已存在业务对象。
2. external_context 只进入 observation 编排上下文，**不**进入 profile positive evidence。
3. 无 evidence 时 Agent **abstain**（诚实 message），不编造偏好。
4. debug 必须区分 agent_planner / tool_execution / external_import 路径。
5. 诊断性、人格化、规训性措辞过滤（继承 V3-E `DIAGNOSTIC_TERMS` 测试扩展）。

## 8. 验收标准

### 8.1 自动测试

- memory backend pytest 全量通过（在 V4-C 79 基线上增加 Agent 测试）。
- 无 report 时 observation abstain。
- 有 report + timeline 时 summary 含 evidenceRefs。
- tool loop 超过 max_steps 时 abstain 或 partial summary（行为需在测试中固定）。
- governance：agent / external import 不 feed profile positive evidence。
- API：observations / agent-actions / external-import confirm 流程。

### 8.2 人工验收清单

- [x] Profile/Timeline 页可触发观察摘要，摘要可展开 evidence。
- [x] Debug 可见 agent tool trace（toolName、reason、refs）。
- [x] mock external import 需确认后才进入 observation 上下文。
- [x] profile 页不因 Agent 摘要新增正向倾向。
- [x] V3-E governance 测试仍全部通过。
- [x] （可选）MCP stdio shell 可调用 internal read-only tools（4 tools + catalog）。

## 9. AI 生成代码顺序（确认后执行）

1. Schema + migration + agent_action / observation / external_import repositories
2. ToolRegistry + internal tool handlers + unit tests
3. ObservationAgentService + mock planner + governance tests
4. observations / external-import API routes
5. Debug trace 扩展 + workflow boundary warnings 更新
6. Frontend 观察摘要 UI + observationApi
7.（可选）stdio MCP server
8. 上升 `07` / `11` / `19` §10.3–10.4 + `15` 记录

## 10. 权威设计文档更新判断

实现开始前建议更新：

- `docs/07`：agent_action_logs、observation_sessions、external_import 表
- `docs/11`：Agent tool registry、observation API、MCP module 契约
- `docs/19` §10.3–10.4：从占位改为实现映射（引用本任务单）
- `agent-frontier-design-docs.md`：`docs/23-Skill与能力沉淀设计文档.md` 可在 V4-D 实现中起草 partial

## 11. 用户确认（已接受）

- [x] 接受 **用户触发观察摘要 + 有限步只读 tool loop**，不做 chat Agent。
- [x] 接受 MCP **先 local stdio internal tools**；外部 OAuth 用 mock import batch 验证治理。
- [x] 接受 Agent / external context **不进入** profile positive evidence（继承 V3 治理）。
- [x] 接受 V4-D **不替换** 现有 `aesthetic_analysis_v1` workflow，Agent 为独立编排层。
- [x] 接受 LLM planner 测试默认 **mock**，Ollama 为可选 runtime（与 V4-A embedding 模式一致）。

## 12. 当前结论

```text
V4-D 实现与人工验收均已完成，状态 accepted / manual_validation_passed。
自动测试：86 passed（memory backend，含 V4-D 新增 7 项）。
§8.2 人工验收全部通过；下一步启动 V4-E（Evaluation Maturity & Governance Validation）。
```
