# V4-0：Long-term Personalized Agent 版本级调研与架构拆分

当前状态：

```text
accepted / no_runtime_implementation
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V4-0 是 V4 的版本级研究与架构闸门，不是功能实现阶段。

本轮目标：

```text
在 V3 Personalized Retrieval / RAG / Evaluation / Observability baseline 之上，明确 V4 长期个性化 Agent、多模态扩展、审美轨迹、知识图谱、MCP 外部上下文、runtime 升级与评估成熟化的能力地图、边界、子阶段拆分与验收标准。
```

为什么必须先做这一轮：

```text
V4 是路线图中的 Agent 化版本，涉及真实模型 runtime、多模态输入、长期轨迹、主动观察、外部数据源和工具调用。如果直接进入实现，容易把 Agent 做成营销包装、把外部上下文写成用户偏好证据，或在 infra 未就绪时过早堆叠知识图谱与 MCP。

V4-0 的职责是先区分：什么是 runtime 地基，什么是长期观察数据面，什么是知识结构，什么是 Agent 行为，什么是外部上下文；并明确哪些能力必须先有真实 embedding / 存储 / 身份边界，哪些可以沿用 V3 的 evidence-first 与 governance 规则。
```

## 2. 上游依据

必须引用：

1. `docs/01-产品概念说明书.md`
2. `docs/02-版本迭代路线图.md`
3. `docs/19-记忆与用户模型设计文档.md`
4. `docs/07-数据结构与系统架构文档.md`
5. `docs/11-模块拆分与接口测试文档.md`
6. `docs/12-开发任务拆分与里程碑计划.md`
7. `docs/13-验证与评估文档.md`
8. `docs/15-迭代执行记录.md`
9. `docs/archive/v3/V3-归档说明.md`
10. `docs/archive/v3/V3-任务拆分与里程碑计划.md`
11. `docs/archive/v3/V3-遗留问题.md`
12. `.cursor/skills/project-development-flow/SKILL.md`

## 3. 对应的 Agent 前沿方向

V4 主要推进：

```text
Multimodal Preference Modeling
Temporal User Profiling
Skill / Capability
Agent Runtime
MCP External Context
Knowledge Graph（轻量）
Evaluation / Observability（成熟化）
Governance
```

V4 继承并不得破坏：

```text
Memory / User Model（V2 baseline）
Preference Explanation（V1–V3）
Personalized Retrieval / RAG for Explanation（V3 baseline）
Evidence-first / Non-diagnostic Expression（横切）
```

V4-0 不进入：

```text
无边界自动行动
未经用户确认的外部数据导入 runtime
没有证据来源的知识图谱关系 runtime
把 Agent 当成营销包装而无 reason / evidence
完整登录系统 / 企业级 IAM（可规划边界，不阻塞 V4 研究）
```

## 4. 版本核心问题

V4 要回答：

```text
系统能否从「单次/阶段性分析工具」升级为「长期、多模态、可解释、有边界的审美观察 Agent」，且每个主动行为都有 reason 和 evidence？
```

拆成更具体的问题：

```text
新模态（音乐、视频、外部收藏）如何进入与图片/文字相同的底层特征 → embedding → 解释链路？
长期审美轨迹如何展示真实历史变化，而不是把两次报告硬拼成人格变化？
workflow step 如何沉淀为可复用 Skill，并被 Agent 在 reason + evidence 约束下调用？
轻量知识图谱如何表达审美概念关系，又不生成无证据的推断边？
MCP 外部上下文如何接入收藏源/笔记库，又 Require 用户确认且不覆盖用户输入证据？
真实 LLM / vision / embedding / ChromaDB runtime 接入后，如何保持 V3 的 trace、evaluation 与 governance？
Agent 主动生成观察摘要或提问时，如何继承 V2/V3 的 not_me / unsure 治理与 profile 更新规则？
```

## 5. 本轮调研问题

版本级调研：

- V4 应先升级 infra runtime，还是先扩展多模态输入 schema？
- 长期轨迹与 Temporal Profiling 应建立在 reports、profile、还是独立 trajectory 对象上？
- Agent 的第一版应是「定期摘要 + 工具调用」，还是「对话式观察助手」？
- MCP 应优先接入哪类外部源（收藏、笔记、资料库），授权与确认流程如何设计？
- 知识图谱是概念解释增强，还是新的偏好证据来源？（预期：前者）
- V3 carry_over 的 grouping stability、failure replay、ChromaDB、外部 RAG、OTel 应落在哪个子阶段？
- V4 子阶段顺序应如何保证「证据优先」不被 Agent 化破坏？

能力级调研：

- 多模态输入最小统一 schema 应包含哪些字段（modality、source、features、embeddingRef）？
- 审美时间轴条目应引用哪些 evidence source（report、comparison、profile item、feedback）？
- Agent tool 列表是否直接复用 V3 function calling 候选（retrieve、generateReport、updateProfile 等）？
- Skill 沉淀的最小单元是 workflow step + prompt contract + validator + tests 吗？
- 知识图谱边需要哪些 mandatory 字段（relationType、sourceEvidence、confidence、disclaimer）？
- MCP tool 与内部 API 的边界：只读先行，还是读写分离服务器？

实现级调研：

- 当前 mock FeatureExtractor / EmbeddingClient 替换策略：interface 一次切换，还是并行 shadow mode？
- ChromaDB 写入应从 input vectors 开始，还是同时索引 knowledge chunks / history summaries？
- 图片文件存储是否先本地目录 + metadata 表，再抽象 object storage？
- 音乐/视频第一版是否接受 metadata-only placeholder（标题、链接、用户备注）而不做真实内容解析？
- LangSmith / OpenTelemetry 是 V4-D 才评估，还是 V4-E 统一接入？
- 匿名用户 + MCP 授权如何共存？是否必须先做持久匿名 ID 或登录？

## 6. 外部调研记录

### 6.1 Temporal profiling 必须区分短期与长期偏好

来源名称：Towards Explainable Temporal User Profiling with LLMs

来源类型：论文 / temporal user profiling

链接或出处：`https://arxiv.org/pdf/2505.00886`

调研问题：

- 用户画像为什么不能只做平均或静态快照？
- 短期与长期偏好如何同时服务解释与推荐？

核心做法：

- 显式区分 recent behaviors 与 persistent tendencies。
- 用自然语言摘要表达时间型 profile，并可用 attention 等方式融合短长期表示。
- 强调 explainability：为何当前判断来自哪些历史片段。

对 V4 的启发：

- V4-B 的审美轨迹不能只堆报告列表，需要 stable / recent / weakening / rejected 的时间语义（继承 V2，扩展到跨报告主题与时间轴）。
- 周期性摘要必须引用具体 report、comparison、feedback evidence，而不是 Agent 自由发挥。

采用结论：

```text
V4-B 采用「时间轴 + 短长期 profile 语义分离」；Agent 摘要只能聚合已有 evidence，不能生成无来源的新偏好。
```

### 6.2 长期 Agent 需要 episodic memory 与 semantic memory 协同

来源名称：PersonaAgent: Bridging Memory and Action for Personalized LLM Agents

来源类型：论文 / personalized LLM agent

链接或出处：`https://arxiv.org/pdf/2506.06254`

调研问题：

- 个性化 Agent 如何同时「记住发生过什么」和「知道用户是什么样」？
- persona / memory 如何影响 tool action？

核心做法：

- 分离 episodic memory（具体交互事件）与 semantic memory（抽象 persona / 稳定知识）。
- persona 作为中介：从 memory 影响 action，action 结果反过来修正 memory。
- 强调 test-time alignment 与动态用户偏好对齐。

对 V4 的启发：

- V4-D Agent 不应只有一个 prompt；需要对接 V2 profile、V3 history/knowledge context、V4 trajectory。
- Agent 调用的 updateProfile / generateObservation 等工具必须写回 evidence，不能只改 prompt 层 persona。

采用结论：

```text
V4-D Agent runtime 复用 V2/V3 已持久化的 memory 事实层；Agent 层只做编排与摘要，不另建平行「黑盒记忆」。
```

### 6.3 Lifelong Agent 需要 multimodal、memory、tool use 与外部知识协同

来源名称：Lifelong Learning of Large Language Model based Agents: A Roadmap

来源类型：论文 / survey roadmap

链接或出处：`https://arxiv.org/html/2501.07278v1`

调研问题：

- LLM Agent 从 demo 到系统缺什么？
- 为什么 multimodal、memory、external knowledge 必须一起规划？

核心做法：

- 长期 Agent 需要 dynamic task adaptation、multimodal integration、memory/knowledge management、external tool use。
- 强调在真实环境中持续学习，同时避免灾难性遗忘与无边界自主。

对 V4 的启发：

- V4 子阶段不能只做 Agent UI；必须先有 V4-A runtime/多模态地基，再有 V4-B 轨迹，再有 V4-C 知识结构，最后 V4-D Agent。
- 「持续学习」在审美系统中应收敛为「证据累积 + 用户确认」，不是无监督自我改写 profile。

采用结论：

```text
V4 采用渐进式 Agent 化：infra → 轨迹 → 知识 → Agent/MCP；不做无边界 lifelong self-modification。
```

### 6.4 MCP 应用 OAuth 2.1、least-privilege 与用户确认

来源名称：Model Context Protocol Authorization / MCP security guides

来源类型：规范 / 工程实践

链接或出处：

- `https://modelcontextprotocol.io/docs/tutorials/security/authorization`
- `https://systemprompt.io/guides/mcp-server-authentication-security`

调研问题：

- MCP 外部上下文最大的产品风险是什么？
- 如何在工具层防止 over-privileged agent？

核心做法：

- MCP 推荐 OAuth 2.1 + PKCE；token 必须校验 audience、scope、过期。
- least-privilege：按 tool 细分 scope；读写工具分离；高风险操作需用户确认。
- 全量 audit log：每次 tool call 关联 user/agent identity。

对 V4 的启发：

- V4-D MCP 第一版只做只读外部源 + 显式用户确认导入；不做 silent background sync。
- 外部收藏/笔记进入系统后仍是 supplementary context，不直接进入 profile positive evidence（继承 V3-B 规则）。

采用结论：

```text
V4-D MCP 先只读、先确认、先 audit；写回业务数据只能走内部 governance 明确的工具。
```

### 6.5 企业 MCP 落地强调标准化集成与安全域隔离

来源名称：How MCP Simplifies Enterprise AI Agent Development in 2025

来源类型：工程实践 / 行业分析

链接或出处：`https://onereach.ai/blog/how-mcp-simplifies-ai-agent-development/`

调研问题：

- MCP 解决的是「集成复杂度」还是「模型能力」？
- 生产部署要先做什么？

核心做法：

- MCP 用统一协议替代 one-off connectors。
- 落地顺序：识别 ROI 场景 → 原型暴露内部工具 → OAuth/RBAC/版本固定/私有 registry → 再扩多 Agent。

对 V4 的启发：

- 审美系统 MCP 第一版应优先「内部工具 MCP 化」（retrieve report、list history、get profile）再接外部收藏源。
- 外部 MCP server 视为 untrusted；导入内容需 sanitization 与 source tagging。

采用结论：

```text
V4-D 先 internal tools MCP surface，再 external collections；不一开始接多个第三方 SaaS。
```

### 6.6 User profiling dynamics 综述强调可解释、隐私与多模态

来源名称：User Profiling and Its Dynamics: A Narrative Review

来源类型：综述论文

链接或出处：`https://journals.sagepub.com/doi/10.1177/30504554251407092`

调研问题：

- 动态 user profiling 有哪些成熟原则？
- 隐私与 explainability 如何进入设计？

核心做法：

- 结合 explicit / implicit 信号；区分短长期；重视 context-awareness 与 explainability。
- 未来方向包括 multimodal integration、privacy preservation、contextual adaptation。

对 V4 的启发：

- V4 必须把「用户可查看 evidence」「可修正/拒绝」继续作为硬约束。
- 多模态扩展先记录 source + user-provided context，不默认爬取或推断私密信息。

采用结论：

```text
V4 动态画像与轨迹保持 explainable + user-auditable；多模态先用户主动输入/确认。
```

## 7. V4 能力地图

### 7.1 Runtime & Infra Foundation

目标：

```text
把 V1–V3 的 mock / heuristic / placeholder 边界升级为可替换的真实 runtime，同时保持 fail-fast 与显性 mock 标记。
```

候选范围：

- 真实 LLM client（report / interpretation generation）。
- 真实 vision / text feature extractor（可分期）。
- 真实 embedding client。
- 图片文件存储与读取。
- ChromaDB 写入与相似度检索（input vectors 起步）。
- 可选：shadow mode 对比 mock 与 real 输出。

关键规则：

- 未配置 real runtime 时保持 mock，且 debug panel 必须可见。
- real runtime 失败时按权威文档决定 fail-fast 或显性降级；不得 silent fallback 到假数据。

### 7.2 Multimodal Inputs & Unified Representation

目标：

```text
在统一「原始输入 → 底层特征 → embedding → 解释」链路下，扩展音乐、视频、外部收藏 metadata 与用户补充上下文。
```

候选输入类型：

- image（真实文件）
- text
- music metadata / link / user note
- video metadata / link / user note
- external collection item（经 MCP 或手动导入）

关键规则：

- 新模态也必须产生可追溯 source refs。
- 第一版可 metadata-only，但 UI/API 必须诚实标注「未做内容解析」。
- 跨模态聚合不得掩盖单模态 evidence 来源。

### 7.3 Aesthetic Trajectory & Temporal Profiling

目标：

```text
让用户看到审美如何随时间变化，而不是只看单次报告或最近两次对比。
```

候选能力：

- 审美时间轴（按时间排列 reports、关键 insights、feedback 事件）。
- 周期性变化摘要（周/月观察，基于已有 reports + comparisons）。
- 长期主题复现、风格迁移提示（必须有 matched features / evidence refs）。
- 扩展 temporal states：stable / recent / weakening / rejected（继承 V2）。

关键规则：

- 轨迹条目必须链接 reportId、insightId、feedbackId 或 comparison evidence。
- 不得把轨迹写成心理/人格发展叙事。

### 7.4 Knowledge Graph & External RAG Runtime

目标：

```text
在 V3 静态审美知识库之上，引入可追溯的审美概念关系与可更新知识检索，但仍只服务解释，不服务偏好证据。
```

候选对象：

- aesthetic concepts（色彩、构图、材质、情绪、主题等）。
- concept relations（related_to、contrasts_with、example_of 等轻量谓词）。
- external / curated knowledge chunks（可向量化入 ChromaDB）。
- source evidence 与 valid_for_features 约束。

关键规则：

- 图谱边必须有 sourceEvidence；无证据不建边。
- 图谱与外部 RAG 不写入 profile positive evidence。
- 与 V3 knowledgeContext 兼容：可升级为 richer items，但不破坏 abstention 语义。

### 7.5 Agent Runtime & Skill / Capability

目标：

```text
在固定 workflow 之上，引入可选择工具、可生成观察摘要、可提出观察问题的审美观察 Agent，且每个行为有 reason 和 evidence。
```

候选 Agent 能力：

- 调用内部工具：分析输入、检索历史、检索知识、生成报告、读取 profile、生成轨迹摘要。
- 定期/触发式观察摘要（非无边界自主）。
- 基于轨迹变化提出观察问题（非诊断式追问）。
- 将成熟 workflow step 沉淀为 Skill（prompt + schema + validator + tests + boundary warnings）。

关键规则：

- Agent plan / action log 必须持久化 reason、toolName、inputRefs、outputRefs。
- Agent 不得绕过 feedback governance 直接改 profile 正向证据。
- 第一版不做 fully autonomous scheduling；需用户显式触发或确认订阅。

### 7.6 MCP External Context

目标：

```text
用标准协议接入外部收藏、笔记或资料库，为分析提供补充上下文。
```

候选来源：

- 用户指定的收藏链接 / 文件夹 metadata。
- 笔记系统只读导出。
- 未来可扩展数据源（含内部 MCP server）。

关键规则：

- 导入必须 user-confirmed；记录 importBatchId、sourceSystem、importedAt。
- 外部内容标记为 external_context，不是 user preference fact。
- OAuth / scope / audit log 按 MCP 最佳实践设计。

### 7.7 Evaluation & Observability Maturity

目标：

```text
补齐 V3 未做的 grouping stability、failure replay，并在真实 LLM/RAG/Agent 场景下扩展 trace 与评估。
```

候选指标与能力：

- grouping stability（同输入簇跨 run 一致性）。
- failure replay（从 analysis_logs + trace 回放失败路径）。
- prompt/version regression checks。
- token / latency / cost metadata（真实 LLM 后）。
- 可选接入 OpenTelemetry / LangSmith（非 V4-0 必做）。

### 7.8 Governance（横切）

V4 必须继承并扩展 V1–V3 治理规则：

- 当前输入 evidence 优先于历史、知识、外部上下文。
- 用户反馈优先于模型/Agent 解释。
- 外部源、图谱、RAG 不写成用户偏好。
- 不输出人格诊断、心理评估、命运判断、身体羞辱或审美规训。
- Agent 每个主动动作可审计、可拒绝、可追踪 evidence。
- 未经用户确认的导入、画像更新、外部写操作一律禁止。

## 8. V4 架构边界

### 8.1 数据边界

V4 可能新增（候选，V4-0 不定最终表结构）：

- `input_files` 或等价文件 metadata 存储。
- `multimodal_inputs` 扩展字段 / 子类型。
- `aesthetic_timeline_events`。
- `observation_summaries`。
- `agent_action_logs`。
- `aesthetic_concepts` / `concept_relations`。
- `external_import_batches` / `external_context_items`。
- `skill_registry` 或 `skill_versions`（可先文档化，后落库）。
- ChromaDB collections：input_vectors、knowledge_vectors（候选）。

V4-0 不决定最终 migration。表结构应在对应实现子阶段确认后写入 `docs/07-数据结构与系统架构文档.md`。

### 8.2 API 边界

V4 可能新增：

- 多模态输入创建与文件上传。
- 审美时间轴查询。
- 观察摘要生成/查询。
- Agent 触发分析或问答（有 reason/evidence 响应）。
- MCP 授权状态与导入批次查询。
- 知识图谱只读查询。
- grouping stability / failure replay 开发查询。

V4-0 不定义最终 API path。契约在子阶段写入 `docs/11-模块拆分与接口测试文档.md`。

### 8.3 Workflow / Agent 边界

V4 可能扩展为：

```text
ingestInput (multimodal)
extractFeatures (real or mock)
generateEmbeddings
writeVectors (ChromaDB)
clusterInputs
retrievePersonalHistory
retrieveAestheticKnowledge
retrieveExternalContext
queryKnowledgeGraph
assembleEvidenceContext
generateInterpretations
generateReport
computeReportEvaluation
saveReportAndTrace
updateTrajectory
updateUserProfile
--- Agent orchestration layer ---
planObservation
executeTool (skill/workflow step)
generateObservationSummary
logAgentAction
```

V4-0 不实现上述 step，只确定方向与依赖顺序。

### 8.4 Frontend 边界

V4 可能新增：

- 多模态输入入口（音乐/视频/外部收藏 metadata）。
- 审美时间轴页。
- 观察摘要页（含 evidence 展开）。
- Agent 观察互动面板（触发式，非强制聊天）。
- MCP 连接与导入确认 UI。
- 知识关系可视化（轻量，只读）。

V4 不应第一版就做复杂 Agent 聊天壳或全功能 dashboard。

## 9. 方案取舍

### 9.1 先 Runtime & Multimodal Foundation，再 Agent

采用：

```text
V4-A 先做真实 runtime / 存储 / ChromaDB / 多模态 schema，V4-D 再做 Agent。
```

原因：

- 没有真实 embedding 与文件读取，多模态与 Agent 工具链无法验收。
- V3 已证明 heuristic pipeline 的 governance；V4 应先换 runtime，再换交互形态。

### 9.2 先 Trajectory，再复杂知识图谱

采用：

```text
V4-B 审美轨迹先于 V4-C 完整知识图谱。
```

原因：

- 用户价值主线是「看到审美变化」，V2 comparison + V3 history 已提供基础。
- 知识图谱依赖概念体系与证据边治理，不应抢在轨迹之前。

### 9.3 先 Internal Tools MCP，再 External Collections

采用：

```text
MCP 先暴露内部只读工具，再接外部收藏源。
```

原因：

- 降低 OAuth / 安全 / 数据清洗复杂度。
- 与当前匿名用户体系冲突较小；外部源导入可强制 batch + confirm。

### 9.4 知识图谱只做解释增强，不做偏好证据

采用：

```text
concept relations 与 external RAG 只进入 explanation / knowledge context，不进入 profile positive evidence。
```

原因：

- 继承 V3-B / V3-E 已验收边界。
- 防止 Agent 用图谱路径绕开 feedback governance。

### 9.5 Agent 先做「观察摘要 + 工具调用」，不做无边界自主

采用：

```text
第一版 Agent 是 evidence-bound observation agent，不是 general autonomous agent。
```

原因：

- 符合产品「解释偏好形成」定位，不是任务执行机器人。
- 更易验收，也更符合 governance。

### 9.6 Evaluation 成熟化放在子阶段尾声

采用：

```text
grouping stability、failure replay、生产级 observability 放 V4-E。
```

原因：

- 需要真实 runtime 与 Agent 路径才有意义。
- 与 V3-E 治理验收对称，形成 V4 最终 closure 前闸门。

## 10. V3 carry_over 重分类（进入 V4 前）

依据 `archive/v3/V3-遗留问题.md` §5：

| 原 carry_over 项 | 建议 V4 归属 | 说明 |
| --- | --- | --- |
| grouping stability | V4-E | 依赖真实 run 与 cluster 稳定性 |
| failure replay | V4-E | 依赖更完整 trace / step detail |
| ChromaDB runtime | V4-A | 先从 input vectors 开始 |
| 真实 LLM / vision / embedding | V4-A | 核心 runtime 地基 |
| 真实图片文件存储与读取 | V4-A | 多模态地基 |
| 外部知识库 RAG runtime | V4-C | 在静态 KB 上升维 |
| LangSmith / OpenTelemetry 生产级 | V4-E | 可选接入，不阻塞 V4-A |
| 复杂 evaluation dashboard / LLM-as-judge | V4-E | 不阻塞早期子阶段 |
| 音乐、视频、外部收藏源 | V4-A（schema）/ V4-D（MCP） | 输入面与接入面拆分 |
| 审美时间轴、知识图谱、Agent、MCP | V4-B / V4-C / V4-D | 按能力地图拆分 |
| 报告详情 API 对象级 user scope | security / V4-A | 与身份边界一并规划 |
| 登录系统或持久匿名 ID | identity / V4-A | 不阻塞研究，但 Agent/MCP 前需方案 |
| integration test 干净 DB | tech-debt / V4-E | 可并行，不阻塞 V4-0 |
| Pydantic / FastAPI alias warnings | tech-debt | 不阻塞 V4-0 |

结论：

```text
无 V3 → V4 blocking issue。
V4-0 可继续，但 V4-D 前必须明确 identity / MCP 授权方案。
```

## 11. V4 子阶段拆分（建议）

建议 V4 拆分为：

### V4-0：版本级研究与架构拆分

状态：

```text
accepted / no_runtime_implementation
```

范围：

- 版本级外部调研。
- 能力地图。
- 架构边界。
- carry_over 重分类。
- 子阶段拆分。
- 验收标准。

### V4-A：Runtime & Multimodal Foundation

目标：

```text
接入真实 LLM / embedding / 图片存储 / ChromaDB 最小路径，并扩展多模态输入 schema（含 metadata-only 音乐/视频/外部收藏占位）。
```

不做：

- 审美时间轴完整产品页。
- Agent 对话壳。
- 外部 MCP 生产接入。
- 知识图谱 runtime。

### V4-B：Aesthetic Trajectory & Temporal Profiling

目标：

```text
基于 V2/V3 已有 reports、comparisons、profile、feedback 构建审美时间轴、周期性摘要与主题复现提示，且全程 evidence-bound。
```

不做：

- 无证据的「人生阶段」叙事。
- 自动修改 profile 的 Agent。

### V4-C：Knowledge Graph & External RAG Runtime

目标：

```text
引入审美概念关系与可更新知识检索（含向量检索），增强解释能力，但不进入 profile positive evidence。
```

不做：

- 无 sourceEvidence 的图谱边。
- 大规模全自动知识 crawl。
- 把图谱关系写成用户偏好。

### V4-D：Agent Runtime & MCP Integration

目标：

```text
实现 evidence-bound 审美观察 Agent（工具调用、观察摘要、观察问题）与 MCP 接入（先 internal tools，后用户确认的外部收藏/笔记只读导入）。
```

不做：

- 无边界自主行动。
- 未经确认的 external write。
- 把 MCP 内容写成 preference evidence。

### V4-E：Evaluation Maturity & Governance Validation

目标：

```text
补齐 grouping stability、failure replay、真实 runtime 下评估与 observability 扩展，并完成 V4 全链路自动 + 人工治理验收。
```

不做：

- V5 级多 Agent 协作。
- 生产级 SaaS 强依赖作为归档硬门槛（可作为可选加分项）。

### V4 final closure / archive gate

目标：

```text
legacy issue audit、archive/v4/ 文档、执行记录更新、V4 正式归档。
```

## 12. V4 版本级验收标准

V4 完成时必须满足：

- 新模态输入能进入统一表征链路，且来源可追溯。
- 审美时间轴能展示真实历史变化，条目可展开 evidence。
- 知识图谱与外部 RAG 只增强解释，不进入 profile positive evidence。
- Agent 每个行为有 reason、tool trace、evidence refs，可审计。
- MCP 导入经用户确认，外部内容标记为 supplementary context。
- 真实 runtime 与 mock 边界在 debug/trace 中可见。
- grouping stability 与 failure replay 至少具备 baseline 实现与测试。
- 页面与 Agent 输出不做人格诊断、心理评估、命运判断或审美规训。
- V4 结束前有 archive gate 和 legacy issue audit。

## 13. 需要上升到权威设计文档的决策

V4-0 reviewed 后，建议将以下长期决策上升到权威设计文档：

- `docs/19-记忆与用户模型设计文档.md`：已创建；汇总 V2/V3 记忆语义，并承载 V4 扩展占位（§10）。
- `docs/07-数据结构与系统架构文档.md`：多模态输入、时间轴、Agent action log、图谱、外部导入对象。
- `docs/11-模块拆分与接口测试文档.md`：runtime adapters、trajectory、graph、agent、mcp 模块边界。
- `docs/13-验证与评估文档.md`：grouping stability、failure replay、Agent governance checks。
- `docs/12-开发任务拆分与里程碑计划.md`：确认 V4-A 为下一实现子阶段。

本轮暂不直接修改 07 / 11 / 13 的稳定设计正文，避免在方案未复核前把候选架构写成正式实现契约。记忆与用户模型语义以 `19` 为权威；V4 相关扩展占位已写入 `19` §10。

## 14. 权威设计文档更新判断

```text
已创建 docs/19-记忆与用户模型设计文档.md，作为 Memory / User Model 语义权威。
07 / 11 / 13 已添加交叉引用；表结构与模块契约仍以各自文档为准。
V4 表结构、API path、Agent tool list、MCP 授权流程仍属候选设计，待 V4-0 确认后再上升到 07 / 11 / 13。
```

## 15. 复核记录

复核日期：

```text
2026-06-17
```

复核范围：

- `docs/02-版本迭代路线图.md` §10 V4 目标、能力范围与不做事项。
- `docs/01-产品概念说明书.md` Agent 前沿方向与长期愿景。
- `docs/archive/v3/` 归档边界与 `V3-遗留问题.md` carry_over 项。
- `docs/07-数据结构与系统架构文档.md` §10.3–10.7 多模态、Agent、图谱、MCP 占位。
- `docs/12-开发任务拆分与里程碑计划.md` 当前执行版本与 V4-0 入口。
- `docs/15-迭代执行记录.md` V3 archive gate 后的下一步。

遗留问题复核：

```text
V3 无 blocking / pending_validation 遗留问题。
V1/V2/V3 carry_over 到 V4 的项已在 §10 重分类。
identity / user scope / MCP 授权需在 V4-D 前落地设计，但不阻塞 V4-0 研究完成。
```

复核结论：

```text
V4-0 草案与路线图、V3 归档边界、既有设计占位一致。
建议子阶段顺序 V4-A → V4-B → V4-C → V4-D → V4-E 合理。
V4-0 仍不应直接实现任何 V4 runtime。
```

## 16. 用户确认记录

复核日期：

```text
2026-06-17
```

用户确认项：

- [x] 接受 V4 子阶段拆分：V4-A → V4-B → V4-C → V4-D → V4-E。
- [x] 接受 V4-A 先做 runtime / 存储 / ChromaDB / 多模态 schema，而不是直接做 Agent。
- [x] 接受知识图谱与外部 RAG 只作 explanation support，不进入 profile positive evidence。
- [x] 接受 MCP 先 internal tools、后用户确认的外部只读导入。
- [x] 接受 Agent 第一版为 evidence-bound observation agent，而非无边界自主 Agent。
- [x] 接受音乐/视频第一版可为 metadata-only placeholder。

## 17. 当前结论

```text
V4-0 版本级研究与架构拆分已获用户确认并接受。
V4 应从 runtime & multimodal foundation（V4-A）开始，而不是直接做 Agent / MCP runtime。
V4-A 任务单见 docs/iterations/v4-a-runtime-multimodal-foundation.md。
```
