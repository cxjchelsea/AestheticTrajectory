# V4-E：Evaluation Maturity & Governance Validation

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-18
```

## 1. 本轮目标

在 V4-A–V4-D 全部 runtime 落地之后，补齐 V3 carry_over 的 **grouping stability** 与 **failure replay**，扩展真实 runtime 下的评估与 debug trace，并完成 **V4 全链路自动 + 人工治理验收**：

```text
cluster_inputs 结果可量化稳定性（pairwise co-membership）
↓
analysis_logs + fallback_events 可组装 failure replay 视图
↓
evaluation / debug trace 扩展（grouping + agent + failure）
↓
test_v4e_governance_validation 覆盖 V4-A–D 横切不变量
↓
boundary_warnings 与 debug panel 反映 V4 已实现能力
↓
（可选）legacy issue audit 预检，为 V4 final closure 做准备
```

本轮完成后，开发者应能：

- 对同一批 input（或同一 job 的 report）查看 **grouping stability score** 与 pairwise 明细，理解 embedding 分组是否稳定。
- 对失败或部分失败的 analysis job 查看 **failure replay**：按 step 顺序展示 failed/skipped 步骤、error、fallback 与 developer message。
- 在 Debug Panel 看到 grouping / agent / failure 相关 trace，且 boundary warnings 不再把已实现的 V4 能力标为 `planned`。
- 运行 `test_v4e_governance_validation.py`，一次性验证 V4-A–D 治理不变量仍成立。
- 确认 V3-E + V4-D 既有 governance 测试仍全部通过。

## 2. 上游版本决策

引用 `docs/iterations/v4-0-long-term-personalized-agent-research.md` §7.7、§V4-E、§12：

- V4-E 在 V4-D 之后、**V4 final closure / archive gate** 之前。
- 必须补齐 grouping stability、failure replay 的 **baseline 实现与测试**。
- 生产级 LangSmith / OpenTelemetry **不是** V4-E 硬门槛（可选加分项）。
- V4 版本级验收要求：真实 runtime 与 mock 边界在 debug/trace 中可见；全链路治理通过。

引用 `docs/archive/v3/V3-遗留问题.md` carry_over：

| 项 | V4-E 处理方式 |
| --- | --- |
| grouping stability 评估指标 | **本轮实现 baseline** |
| failure replay 记录与回放 | **本轮实现 baseline**（基于现有 analysis_logs，不强制 step I/O 全量持久化） |
| LangSmith / OpenTelemetry 生产级 | **不做**；保留 boundary warning |
| 复杂 evaluation dashboard / LLM-as-judge | **不做** |
| integration test 干净 DB | **文档化 + 可选 fixture**；不阻塞 V4-E |

引用 `docs/13-验证与评估文档.md` §15.1、§15.2、§15.3：

- grouping stability：相同或相似输入的分组是否稳定。
- observability 应能回答「系统为什么生成这条洞察 / 为什么在这一步失败」。
- fallback 必须显性化、可追踪、可测试。

引用 `docs/19-记忆与用户模型设计文档.md` §8、§10：

- V4 扩展不能绕开 evidence-first 与 profile 治理不变量。
- Agent / external / knowledge / timeline 均不得进入 profile positive evidence。

## 3. 本轮解决什么问题

本轮解决：

```text
如何在不大改现有 workflow 的前提下，把 V3 延后的评估指标与失败回放落地，并一次性验收 V4 全链路治理？
```

本轮不解决：

- V4 final closure / archive gate 本身（V4-E 完成后单独执行）。
- 生产级 OpenTelemetry / LangSmith pipeline。
- LLM-as-judge、复杂 evaluation dashboard、token/cost 大盘。
- grouping stability 的跨用户长期统计或 ML 聚类调参平台。
- failure replay 的「一键重跑 workflow」自动化（首版只读回放视图）。
- V5 级多 Agent 协作。
- 登录系统 / 持久匿名 ID（identity carry_over 仍延后）。

## 4. 当前实现快照（V4-E 起点）

| 能力 | 当前状态 |
| --- | --- |
| Report evaluation | V3-C：`evidenceCoverage`、`feedbackHitRate`、`schemaPassRate` 等；**无** grouping stability |
| Debug trace | V3-D：`retrievalTrace`、`evaluationTrace`、`fallbackEvents`；**无** grouping / failure replay 分区 |
| analysis_logs | 每 step 有 status / errorType / errorMessage / latency；**无** step 级 input/output 快照 |
| cluster_inputs | `build_similarity_groups` + 结果写入 `report.similarityGroups` |
| Agent trace | V4-D：`agent_action_logs` + ProfilePage tool trace；**未**接入 analysis debug |
| boundary_warnings | Agent/MCP 仍标 `planned`（与 V4-D 已实现状态不一致） |
| V4 governance 测试 | 分散在 `test_v4d_governance.py`、各子阶段测试；**无** 统一 V4-E 横切套件 |
| pytest 基线 | 86 passed（memory backend） |

## 5. 外部调研与方案选择

调研层级：

```text
版本级：引用 v4-0 §7.7、§10 carry_over 重分类
能力级：grouping stability 度量方式、failure replay 最小可行数据
实现级：复用 report + analysis_logs vs 新表、API 形态
```

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| grouping stability 怎么量？ | **Pairwise co-membership consistency**：对同一 input 集合，比较两次 cluster 结果中每对 input 是否同组；score = 一致 pair 数 / 总 pair 数 |
| 比较哪两次 run？ | **Baseline A**：同一 job 的 report.groups vs 用相同 embeddings 重新调用 `build_similarity_groups`（确定性复算）；**Baseline B**（可选）：同一 user 两次 job 的 input 集合交集 |
| 是否需要新表？ | **首版不需要**；从 report JSON + embeddings metadata 复算；可选把 score 写入 evaluation metrics |
| failure replay 最小数据？ | **analysis_logs + fallback_events + workflowTrace** 足够组装只读 replay；不强制 step I/O 持久化 |
| Agent 评估放哪？ | **独立 observation evaluation** + debug 引用 `agent_action_logs`；不混入 report evaluation |
| OTel / LangSmith？ | **拒绝**作为 V4-E 必做；boundary warning 保持 `not_used` / 文档说明 |
| 全链路治理怎么验？ | 新增 `test_v4e_governance_validation.py`，聚合 V4-A–D 关键不变量 + grouping/failure API smoke |

### 5.2 外部调研记录

#### 记录 1：Cluster stability in recommendation / profiling

来源名称：Towards Explainable Temporal User Profiling with LLMs（v4-0 §6.1 引用链）

来源类型：论文 / 工程实践

调研问题：

- 分组/画像稳定性应如何向开发者暴露，而不是伪装成用户偏好事实？

核心做法：

- 区分 **session-level structure** 与 **stable preference**；稳定性指标带 disclaimer。

对 V4-E 的启发：

- grouping stability score 必须附带 uncertainty / disclaimer，不得写入 profile。

采用结论：

```text
GroupingStabilityResult 为 dev/evaluation 指标，supplementary only。
```

#### 记录 2：Failure replay / trace debugging

来源名称：OpenTelemetry trace replay 模式 & V3-D analysis_logs 设计

来源类型：工程实践 + 项目既有设计

调研问题：

- 没有 step 级 I/O 持久化时，能否做有用的 failure replay？

核心做法：

- 用 ordered step log + error + fallback event 重建失败路径；标注「只读回放，非自动重跑」。

对 V4-E 的启发：

- V4-E 实现 **FailureReplayView**，不引入重跑引擎。

采用结论：

```text
GET failure-replay 返回 step 时间线 + errors + fallbacks；测试用 fixture failed job。
```

#### 记录 3：Evaluation maturity without LLM-as-judge

来源名称：docs/13 §15、V3-C baseline metrics

来源类型：项目权威文档

调研问题：

- V4-E 如何避免 scope creep 到复杂 evaluation 平台？

核心做法：

- 只补 V3 carry_over 两项 + 扩展 trace；dashboard / judge 明确不做。

对 V4-E 的启发：

- 指标数量控制在 2 个新能力 + 1 个 governance 套件。

采用结论：

```text
Baseline implementation + tests，不做 evaluation SaaS。
```

### 5.3 方案对比

#### Grouping stability

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 仅单元测试 cluster 确定性 | 最简单 | 无 API / 无可观测性 | 作为内核测试 |
| B 复算 + pairwise score + API | 可调试、可展示 | 需 embeddings 可读 | **采用** |
| C 跨 session 长期 stability 面板 | 产品化 | 超 V4-E | 拒绝 |

#### Failure replay

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 扩展 analysis_logs 存 step I/O | 完整 replay | migration 大、超 scope | 拒绝 |
| B logs + fallback 组装只读视图 | 复用 V3-D | 不能重放中间态 | **采用** |
| C 接入 LangSmith trace | 生产级 | 超 V4-E | 推迟 |

#### V4 治理验收

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 仅人工 checklist | 轻 | 易遗漏 | 拒绝 |
| B 统一 `test_v4e_governance_validation.py` | 可回归 | 需维护 | **采用** |
| C 端到端 browser 测试 | 全面 | 工程量大 | 推迟到 closure |

## 6. 系统边界

### 6.1 必做

- [x] `GroupingStabilityService`：对 report 或 job 计算 pairwise stability（复算 cluster vs persisted groups）。
- [x] `FailureReplayService`：从 analysis_logs + fallback_events 组装 failure replay 视图。
- [x] Schema：`GroupingStabilityResult`、`FailureReplayResponse`；扩展 `ReportEvaluationMetrics` 或独立 evaluation 端点。
- [x] API：
  - `GET /api/reports/{report_id}/grouping-stability`
  - `GET /api/analysis-jobs/{job_id}/failure-replay`
- [x] Debug 扩展：`groupingStabilityTrace`（或并入 evaluationTrace）、`failureReplay`（failed job 时）；更新 `boundary_warnings`（Agent/MCP → `dev_only` 说明）。
- [x] `test_v4e_governance_validation.py`：V4-A–D 横切治理 + grouping/failure API。
- [x] 前端 Developer Debug Panel：Grouping Stability + Failure Replay 两个只读分区（dev 环境）。
- [x] 上升 `docs/13` §15.1.6–15.1.7（V4-E checks）、`docs/15` §24、`docs/12` 下一步。

### 6.2 可选

- [ ] 同一 user 跨 job grouping 比较（Baseline B）。
- [ ] `report_json.evaluationMetrics.groupingStability` 持久化（workflow step 或 on-read 计算）。
- [ ] legacy issue 预检脚本 / 文档段落（指向 V4 closure）。

### 6.3 明确不做

- LangSmith / OpenTelemetry runtime 接入。
- LLM-as-judge、evaluation dashboard、token/cost 大盘。
- failure replay 一键重跑 workflow。
- 修改 cluster 算法或 similarity threshold（除非测试发现确定性 bug）。
- V4 archive / closure 文档包（留给 closure gate）。

## 7. 架构影响

### 7.1 数据模型（拟）

无强制新表。可选扩展：

```text
ReportEvaluationMetrics.groupingStability: float | null
ReportEvaluationMetrics.groupingStabilityNote: str | null
```

`FailureReplayResponse` 为聚合视图，不持久化。

### 7.2 API 设计（拟）

| 路径 | 方法 | 说明 |
| --- | --- | --- |
| `/api/reports/{report_id}/grouping-stability` | GET | 返回 score、pairDetails、disclaimer、recomputedGroups |
| `/api/analysis-jobs/{job_id}/failure-replay` | GET | 返回 steps[]（status、error、fallbacks）；成功 job 返回 empty + message |
| `/api/analysis-jobs/{job_id}/debug` | GET | 扩展 groupingStabilityTrace、failureReplay（与上同源） |

权限：与现有 report / analysis-jobs 一致（匿名 dev 环境）。

### 7.3 模块与目录（拟）

```text
backend/app/schemas/evaluation_maturity.py
backend/app/services/grouping_stability.py
backend/app/services/failure_replay.py
backend/app/services/observability_trace.py          # 扩展
backend/app/services/analysis_job_service.py         # boundary_warnings 更新
backend/app/api/routes/evaluation_maturity.py        # 或并入 reports / analysis_jobs
backend/app/tests/unit/test_grouping_stability.py
backend/app/tests/unit/test_failure_replay.py
backend/app/tests/unit/test_v4e_governance_validation.py
frontend/src/pages/ReportDetailPage.tsx              # debug 分区
frontend/src/types/aesthetic.ts
frontend/src/services/evaluationApi.ts               # 可选
```

### 7.4 Grouping stability 算法（拟）

```text
inputs = report.low_level_features[].input_id
groups_persisted = partition from report.similarityGroups
groups_recomputed = build_similarity_groups(inputs, features, embeddings, threshold)
pairs = all C(n,2) for n >= 2 else empty
for each pair (a,b):
  same_persisted = co_members(a,b, groups_persisted)
  same_recomputed = co_members(a,b, groups_recomputed)
  consistent = same_persisted == same_recomputed
score = consistent_count / len(pairs)  # n<2 或 no groups → null + message
```

Disclaimer 固定包含：「该指标衡量本次 clustering 复算一致性，不代表长期偏好或绝对分类。」

### 7.5 Failure replay 组装（拟）

```text
logs = analysis_logs ordered by started_at
fallbacks = fallback_events by stepId
steps = [
  { stepId, status, errorType, errorMessage, latencyMs,
    fallbacks: [...], developerSummary }
]
failed = any status == failed
return { jobId, failed, steps, replayDisclaimer: "只读回放，非自动重跑" }
```

### 7.6 治理不变量（V4-E 验收重点）

1. grouping stability 指标 **不进入** profile positive evidence。
2. failure replay 不得伪造成功步骤或掩盖 Level 0 失败。
3. Agent / knowledge / timeline / external context 仍不 feed profile positive evidence（继承 V3-E + V4-D）。
4. 诊断性、人格化、规训性措辞过滤（扩展 `DIAGNOSTIC_TERMS` 到 evaluation summary / replay message）。
5. mock / heuristic runtime 边界在 debug 中仍可见；不把 mock 标为 production capability。

## 8. 验收标准

### 8.1 自动测试

- memory backend pytest 全量通过（在 V4-D 86 基线上增加 V4-E 测试）。
- 同一 report 复算 grouping stability → score = 1.0（确定性路径）。
- 人为扰动 mock groups（测试 fixture）→ score < 1.0 且 pairDetails 可解释。
- input 数 < 3 → grouping stability 为 null + 诚实 message。
- failed job fixture → failure-replay 含 failed step + error + fallback（如有）。
- success job → failure-replay empty + message。
- `test_v4e_governance_validation.py` 全部通过。
- V3-E + V4-D governance 测试仍全部通过。

### 8.2 人工验收清单

- [x] 报告 Debug Panel 可见 Grouping Stability 分区（score / disclaimer）。
- [x] 失败 job（或 dev 注入失败）Debug Panel 可见 Failure Replay 步骤链。
- [x] boundary_warnings 中 Agent/MCP 不再标为「Planned for V4」与已实现矛盾。
- [x] grouping stability / failure replay API 返回结构与 disclaimer 正确。
- [x] Profile 页不因 evaluation 新指标新增正向倾向。
- [x] V4-A–D 主路径（分析、timeline、knowledge、observation）回归无退化。

## 9. AI 生成代码顺序（确认后执行）

1. Schema + `GroupingStabilityService` + unit tests
2. `FailureReplayService` + unit tests + failed-job fixture
3. API routes + integration tests
4. observability_trace / analysis_job_service 扩展 + boundary_warnings 修正
5. `test_v4e_governance_validation.py`
6. Frontend Debug Panel 分区
7. 上升 `docs/13` §15.1.6–15.1.7 + `docs/15` §24 + `docs/12`

## 10. 权威设计文档更新判断

实现开始前建议更新：

- `docs/13-验证与评估文档.md`：§15.1.6 V4-E grouping stability；§15.1.7 V4-E failure replay & full governance
- `docs/11-模块拆分与接口测试文档.md`：evaluation maturity API 契约（实现时写入）
- `docs/07-数据结构与系统架构文档.md`：**不涉及**新表（首版）；若持久化 groupingStability 到 metrics 再补字段说明

本轮暂不修改 `docs/19` 正文（evaluation 语义已在 §8 覆盖）；V4 closure 时再汇总。

## 11. 用户确认（待确认）

- [x] 接受 **pairwise co-membership + 复算 cluster** 作为 grouping stability baseline，不做长期 cross-user 统计平台。
- [x] 接受 failure replay 为 **只读 logs 组装视图**，不做一键重跑、不强制 step I/O 持久化。
- [x] 接受 V4-E **不接入** LangSmith / OpenTelemetry 生产 pipeline（保持 boundary warning）。
- [x] 接受通过 **`test_v4e_governance_validation.py`** 作为 V4 横切治理回归套件，人工验收 §8.2 后进入 V4 final closure gate。
- [x] 接受 Debug Panel 仅增加 **两个只读分区**（Grouping Stability、Failure Replay），不做 evaluation dashboard。

## 12. 当前结论

```text
V4-E 实现与人工验收均已完成，状态 accepted / manual_validation_passed。
自动测试：96 passed（memory backend，含 V4-E 新增 10 项）。
§8.2 人工验收全部通过；下一步执行 V4 final closure / archive gate。
```
