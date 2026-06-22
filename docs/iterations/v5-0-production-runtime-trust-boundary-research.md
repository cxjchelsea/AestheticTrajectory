# V5-0：Production Runtime & Trust Boundary 版本级调研与架构拆分

当前状态：

```text
user_confirmed / gate_passed
```

创建日期：

```text
2026-06-22
```

## 1. 本轮定位

V5-0 是 V5 的版本级研究与架构闸门，**不是功能实现阶段**。

本轮目标：

```text
在 V4 long-term personalized agent baseline 之上，明确 V5「可部署运行时 + 用户信任边界」的能力地图、边界、子阶段拆分与验收标准。
```

为什么必须先做这一轮：

```text
V4 已建立 evidence-bound Agent、时间轴、知识图谱、MCP mock 治理与 evaluation baseline，但核心 workflow 仍为 mock/heuristic；
用户身份为匿名 dev 模式；外部 MCP 为 mock import batch；Chroma/Ollama 不可达时存在 hard fail 路径。

若直接进入「加功能」，容易堆出无法部署的 demo，或在不解决 identity / real runtime 的前提下接 OAuth MCP，破坏 V1–V4 治理。

V5-0 的职责是：从 archive/v4 遗留问题与产品长期目标中，选出 V5 的单一 major 矛盾，拆成有限子阶段，并明确 V5 不做 multi-agent 平台化。
```

## 2. 上游依据

必须引用：

1. `docs/01-产品概念说明书.md`
2. `docs/02-版本迭代路线图.md` §11（V5 正式描述）、§14（当前版本判断）
3. `docs/19-记忆与用户模型设计文档.md`
4. `docs/20-多模态偏好建模设计文档.md`
5. `docs/archive/v4/V4-归档说明.md`
6. `docs/archive/v4/V4-遗留问题.md`
7. `docs/iterations/v4-0-long-term-personalized-agent-research.md`
8. `docs/12-开发任务拆分与里程碑计划.md`
9. `docs/13-验证与评估文档.md`
10. `docs/15-迭代执行记录.md` §25

## 3. 对应的 Agent 前沿方向

V5 主要推进：

```text
Multimodal Preference Modeling（真实 LLM / 可选 vision 路径）
Skill / Capability（workflow → 可替换 runtime adapter，非完整 Skill Library）
Evaluation / Observability（生产级可选项 + 降级一致性）
Governance（identity 边界扩大后的治理回归）
MCP External Context（OAuth / 生产只读接入）
```

V5 继承并不得破坏：

```text
Memory / User Model（V2–V4 baseline）
Personalized Retrieval / RAG / Knowledge Graph（V3–V4）
Agent Runtime evidence-bound 观察（V4-D）
Evaluation baseline（V4-E）
Evidence-first / Non-diagnostic Expression（横切）
```

V5-0 明确不做：

```text
V5 级 multi-agent 协作 / 编排平台
复杂 evaluation dashboard / LLM-as-judge 作为主验收
企业级 IAM / SSO 全家桶
无边界 chat Agent 或自主定时任务
把 external / LLM 输出直接写入 profile positive evidence
```

## 4. 版本核心问题

V5 要回答：

```text
系统能否在真实模型 runtime 与用户/数据信任边界就绪的前提下，成为「可部署、可接真实外部源、可运维降级」的审美观察系统，且仍满足 V1–V4 全部治理不变量？
```

拆成更具体的问题：

```text
mock/heuristic workflow 的哪些 step 应优先替换为真实 LLM，且如何保持 schema + evidence 契约？
持久用户身份（登录或持久匿名 ID）如何与现有 user_anonymous dev 模式共存？
报告 / profile / timeline API 的对象级 user scope 如何实现？
OAuth MCP 外部只读导入如何在 V4-D mock 治理之上落地？
Chroma / Ollama 不可达时，knowledge 等步骤如何与 write_vectors 一样 graceful degrade？
可选 OpenTelemetry / LangSmith 接入是否作为 V5 硬门槛还是加分项？
音乐/视频是否仍 metadata-only，还是引入轻量内容解析（ASR/帧 caption）？
```

## 5. 本轮调研问题

### 5.1 版本级

- V5 的单一 major 矛盾是 runtime、identity、还是 MCP？→ **结论：runtime + identity 为地基，MCP 为 V5-C，三者顺序不可颠倒。**
- V4 carry_over 中哪些进 V5 必做、哪些进 tech-debt、哪些继续 V6+？
- V5 子阶段数量应控制在几条以避免 scope creep？→ **建议 V5-A → V5-E（5 个子阶段 + closure），与 V3/V4 对称。**
- 是否在 V5 正式起草 `docs/23-Skill与能力沉淀设计文档.md` partial？

### 5.2 能力级

- Real report runtime：先替换 `MockInterpretationGenerator` + insight 生成，还是全链路 LLM？
- Vision：是否与 text LLM 同阶段，还是 V5-B 仅 text、vision 放 V5-C 或 V6？
- Identity：magic link / 持久 anonymous cookie / 本地 dev bypass 三模式如何设计？
- MCP OAuth：先支持哪一种外部源（Notion read-only、URL bookmark、本地 folder metadata）？

### 5.3 实现级

- LLM provider：延续 openai/ollama factory 模式，是否增加统一 `LLMRuntime` interface？
- Prompt contract：V5-B 是否强制 JSON schema + validator，失败则 fail fast（Level 0）？
- Database integration tests：是否 V5-D 引入 testcontainers / 干净 DB fixture？
- Pydantic alias warnings：V5-D tech-debt 批次清理？

## 6. V4 遗留问题重分类（进入 V5 前）

来源：`docs/archive/v4/V4-遗留问题.md` §5

| 原 carry_over | V5 分类 | 目标子阶段 / 说明 |
| --- | --- | --- |
| 真实 vision / LLM report runtime | **V5 必做** | V5-B（text 优先；vision 可选同阶段或 V5-C 前） |
| 登录 / 持久匿名 ID | **V5 必做** | V5-A |
| 报告 API 对象级 user scope | **V5 必做** | V5-A |
| 生产 OAuth MCP + 外部 SaaS | **V5 必做** | V5-C（1–2 个源，只读） |
| Chroma 不可达时 knowledge 500 | **V5 必做** | V5-D resilience |
| LangSmith / OpenTelemetry | **V5 可选** | V5-D 加分项，非归档硬门槛 |
| 复杂 evaluation dashboard / LLM-as-judge | **V6+ / wont_fix V5** | 不进入 V5 |
| failure replay 一键重跑 | **V6+** | V4-E 只读回放已足够 |
| cross-user grouping stability 平台 | **V6+** | V4-E pairwise 已足够 |
| 音乐/视频真实内容解析 | **V5 可选 / V5-C 边界** | 首版仍 metadata-only；可选 ASR/caption  spike 不阻塞 |
| integration test 干净 DB | **V5-D tech-debt** | |
| Pydantic / FastAPI alias warnings | **V5-D tech-debt** | |
| V5 级 multi-agent | **wont_fix V5** | 明确不做 |

## 7. 能力地图（V5 候选）

```text
V4 baseline（已归档）
├── mock/heuristic aesthetic_analysis_v1
├── user_anonymous + 无对象级 scope
├── mock external import batch
├── optional ollama/chroma（硬 fail 路径仍存在）
└── evaluation / agent / graph / timeline 已落地

V5 目标增量
├── V5-A Identity & Access：持久用户 ID、API scope、dev bypass
├── V5-B Real Report Runtime：LLM structured report（schema + evidence 契约）
├── V5-C Production MCP：OAuth + 1–2 只读外部源
├── V5-D Resilience & Observability：降级一致性、可选 OTel、tech-debt
└── V5-E V5 Governance Validation：全链路治理回归 + 人工验收
```

## 8. 子阶段拆分（候选，待 §11 确认）

### V5-A：Identity & Access Boundary

目标：

```text
建立持久用户身份与 API 对象级 scope，使 report/profile/timeline/agent 数据在 multi-user 场景下可隔离；dev 环境保留 bypass。
```

必做：

- 用户身份方案（持久 anonymous ID 或轻量 auth 二选一为主路径）。
- `user_id` 贯穿 API 与 repository 查询边界。
- migration + 现有 `user_anonymous` 数据迁移或兼容策略。

不做：

- 企业 SSO、复杂 RBAC、多租户计费。

### V5-B：Real Report Runtime

目标：

```text
用真实 LLM（+ 可选 vision）替换 mock interpretation / insight 生成路径，保持 Prompt Contract、schema validation 与 evidenceRefs 不变量。
```

必做：

- `LLMRuntime` / provider factory（openai / ollama 至少一种生产路径）。
- workflow step 替换策略：shadow mode 或直接切换（需在子阶段任务单定）。
- governance 测试扩展：LLM 输出仍不得做人格诊断、不得伪造 evidence。

不做：

- 无 schema 的自由文本报告。
- LLM 输出直接进入 profile positive evidence。

### V5-C：Production External Context（MCP OAuth）

目标：

```text
在 V4-D mock import 治理之上，接入 1–2 个真实 OAuth MCP 只读源；用户 confirm 流不变。
```

必做：

- OAuth 2.1 + PKCE 最小实现或委托成熟 MCP client。
- external import batch 与 V4-D 模型兼容。
- Agent / workflow 仍标记 supplementary context。

不做：

- 未经确认的 background sync。
- external write、自动 profile 更新。

### V5-D：Resilience, Observability & Tech-debt

目标：

```text
对齐降级语义（Chroma/knowledge/LLM 失败路径）、可选 OTel、清理 V4 已知 tech-debt。
```

必做：

- knowledge vector store init 与 write_vectors 同级 graceful degrade。
- integration test 干净 DB 方案（或 documented fixture）。
- Pydantic alias warnings 批次清理（若影响 schema 契约则优先）。

可选：

- OpenTelemetry exporter / LangSmith trace（dev-only 边界）。

不做：

- 复杂 evaluation SaaS dashboard。

### V5-E：V5 Governance Validation & Closure Prep

目标：

```text
test_v5e_governance_validation + 人工全链路验收；为 V5 archive gate 准备。
```

必做：

- 横切治理套件（identity + LLM + MCP + V4 回归）。
- 人工验收清单 §8.2 级。

不做：

- V5 archive 本身（单独 closure gate 任务）。

### V5 final closure / archive gate

目标：

```text
legacy issue audit、archive/v5/、执行记录更新、V5 正式归档。
```

## 9. 子阶段依赖顺序

```text
V5-A（identity）
→ V5-B（real LLM report，依赖稳定 user scope 与 audit）
→ V5-C（OAuth MCP，依赖 V5-A 用户确认身份）
→ V5-D（resilience / tech-debt，可与 V5-C 部分并行，建议 V5-C 后）
→ V5-E（治理验收）
→ V5 final closure
```

## 10. V5 版本级验收标准（候选）

V5 完成时必须满足：

- 真实 LLM 路径可生成报告，且 insight `evidenceRefs` 仍只指向当前 inputs。
- 用户身份持久化；跨 user 不可读取他人 report/profile（对象级 scope）。
- 至少 1 个真实 OAuth MCP 只读源经用户 confirm 后进入 external_context。
- Chroma/LLM 不可达时，核心 workflow 不 500（Level 0 仍 fail fast）。
- V4 治理测试 + V5 新增治理测试全部通过。
- mock / real runtime 边界在 debug 中可见。
- 页面与 LLM 输出不做人格诊断、心理评估、命运判断或审美规训。
- V5 结束前有 archive gate 和 legacy issue audit。

## 11. 权威设计文档更新判断

V5-0 确认后、V5-A 实现前建议：

- `docs/02-版本迭代路线图.md`：§11 V5 已写入；§12 依赖链与 §14 当前判断已更新。
- `docs/07`：用户/会话表或 scope 字段（V5-A 定稿后）。
- `docs/11`：identity API、LLM runtime adapter、OAuth MCP 契约（各子阶段上升）。
- `docs/13`：V5 治理检查项。
- `docs/19` / `docs/20`：若 identity 或 multimodal runtime 语义变更。
- `docs/23-Skill与能力沉淀设计文档.md`（拟）：V5-B 前 partial 起草（registry 已登记 pending）。

本轮 V5-0 **不修改** 07/11 稳定正文，仅记录判断。

## 12. 用户确认（已接受，2026-06-17）

- [x] 接受 V5 major 主题为 **Production Runtime & Trust Boundary**（真实 LLM + identity + OAuth MCP + resilience），而非 multi-agent 平台。
- [x] 接受子阶段顺序 **V5-A → V5-B → V5-C → V5-D → V5-E → archive**。
- [x] 接受 V5-B **先 text LLM report**，vision 为可选同阶段或延后，不阻塞 V5-A/C。
- [x] 接受 OAuth MCP **1–2 个只读外部源**，继承 V4-D confirm 治理，不做 silent sync。
- [x] 接受 LangSmith / OTel 为 **V5-D 可选加分项**，非 V5 归档硬门槛。
- [x] 接受 **不做** V5 multi-agent、LLM-as-judge dashboard、企业 IAM。
- [x] 确认后启动 V5-A 任务单（不跳过子阶段 gate 直接写代码）。

## 13. 当前结论

```text
V5-0 版本级调研与用户确认已完成，状态 user_confirmed / gate_passed。
下一子阶段：V5-A Identity & Access Boundary（任务单 v5-a-identity-access-boundary.md）。
docs/02 §11 / §14、docs/12、docs/15 §26 已同步。
pytest 基线 96 passed。
```
