# V3-C：Evaluation Metrics Baseline

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V3-A / V3-B 已具备 history context 与 knowledge context 的基础上，实现最小 evaluation metrics baseline：

```text
报告生成 workflow 计算基础质量指标
↓
指标写入 report_json.evaluationMetrics
↓
GET /api/reports/{report_id}/evaluation 可返回最新指标（含 feedback）
↓
报告详情页展示“质量评估”
```

## 2. 上游版本决策

引用 `docs/iterations/v3-0-personalized-retrieval-research.md`：

- V3-C 实现 evidence coverage、retrieval coverage、unsupported insight count、feedback hit rate、schema pass rate。
- 不做完整 RAGAS runtime。
- 不做在线 LLM-as-judge。
- 不做复杂 evaluation dashboard。

引用 V3-A / V3-B 已落地边界：

- retrieval items 需 relevance gate 与 source refs。
- evaluation 应能反映 grounding / retrieval 分层，而不是单一总分。

## 3. 外部调研与方案选择

本节在实现 V3-C 前完成；2026-06-17 流程重跑后，调研结论已回写实现。

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.1、§6.3、§6.4
能力级：evaluation metrics baseline、retrieval/generation 分层评估
实现级：deterministic metrics、schema pass rate、feedback refresh、read API
```

### 3.1 调研问题

- mock / heuristic pipeline 下，哪些 RAG 指标可以先做 deterministic baseline？
- evidence coverage 与 unsupported insight count 应如何对应 faithfulness / grounding？
- retrieval coverage 应如何覆盖 V3-A history context 与 V3-B knowledge context？
- schema validation 的 `not_recorded` 是否应计入 pass rate 分母？
- 用户 feedback 后，evaluation 应如何刷新而不重跑 generation workflow？

### 3.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：RAG 评估必须拆分 retrieval 与 generation

来源名称：Evaluation of Retrieval-Augmented Generation: A Survey

来源类型：论文 / RAG evaluation survey

链接或出处：`https://arxiv.org/html/2405.07437v2`

调研问题：

- 为什么不能只看“报告好不好”一个总分？
- baseline 至少应覆盖哪些 failure mode？

核心做法：

- RAG evaluation 需要分别看 retrieval quality、answer quality、grounding / faithfulness。
- end-to-end score 无法定位失败来自检索还是生成。
- 需要关注 unsupported claims 与 retrieved documents 和最终输出的关系。

对 V3-C 的启发：

- baseline 至少包含 evidence coverage、retrieval coverage、unsupported insight count、schema pass rate。
- history / knowledge context 的 source ref 覆盖率单独计入 retrievalCoverage。
- 不做单一 LLM 质量分。

不能照搬：

- 不引入完整 RAG benchmark suite。
- 不做 latency / robustness 全量评估。

采用结论：

```text
V3-C 采用分层 deterministic metrics：generation grounding + retrieval coverage + workflow schema pass rate。
```

#### 记录 2：RAGAS faithfulness 思想的本地化

来源名称：RAGAS: Automated Evaluation of Retrieval Augmented Generation

来源类型：论文 / RAG evaluation framework

链接或出处：`https://arxiv.org/html/2309.15217v1`

调研问题：

- 没有 ground truth 时，faithfulness 如何本地化？
- evidence coverage 是否应只统计“有 refs”，还是“refs 真正绑定当前输入”？

核心做法：

- faithfulness 检查 answer claims 是否被 retrieved / primary context 支持。
- context precision 关注 retrieved context 是否有效、可引用。

对 V3-C 的启发：

- 初版 `evidenceCoverage` 只要 insight 有任意 evidenceRefs 就算 covered，会与 `unsupportedInsightCount` 冲突。
- 调研后应将 evidence coverage 定义为“至少绑定一个当前 input evidenceRef 的 insight 占比”。
- `retrievalCoverage` 继续作为 context precision proxy：history/knowledge items 是否都带 sourceRefs。

不能照搬：

- 不调用 RAGAS LLM judge。
- 不做 context recall。

采用结论：

```text
evidenceCoverage 与 unsupportedInsightCount 共用同一 grounding 规则：evidenceRefs 必须绑定当前 input。
```

#### 记录 3：claim-level grounding 的最小实现

来源名称：RAG evaluation: Expert guide

来源类型：工程实践 / RAG evaluation guide

链接或出处：`https://www.n-ix.com/rag-evaluation/`

调研问题：

- 为什么 insight-level 检查比整份报告打分更适合 V3-C？

核心做法：

- grounding error 包括 unsupported facts、过度推断、错误合成多个片段。
- automatic baseline 可先抓“无 evidence 或 evidence 不绑定 primary input 的 insight”。

对 V3-C 的启发：

- `unsupportedInsightCount` 保持 insight-level 检查。
- disclaimer 必须说明指标用于开发期质量观察，不是人格/心理判断。

不能照搬：

- 不做 sentence-level entailment model。
- 不做通用事实真伪检查器。

采用结论：

```text
V3-C 以 insight-level evidence binding 作为最小 grounding 检查。
```

#### 记录 4：schema pass rate 与 feedback 后 refresh

来源名称 1：Pydantic — Validation

来源类型 1：框架文档 / schema validation

链接或出处 1：`https://docs.pydantic.dev/latest/concepts/validation/`

来源名称 2：RAG evaluation guide — reference-free vs reference-based split

来源类型 2：工程实践 / eval 设计

链接或出处 2：`https://learnwithparam.com/blog/ragas-evaluation-rag-pipelines-practical-guide`

调研问题：

- workflow 中 `not_recorded` 是否应拉低 schema pass rate？
- feedback 后如何 refresh evaluation？

核心做法：

- 结构化 pipeline 应把 schema validation 作为可观测步骤。
- reference-free metrics 适合高频自动评估；user feedback 是后置信号，应通过 read API 刷新。
- 不应把“未记录步骤”误当成“失败步骤”。

对 V3-C 的启发：

- 初版 schemaPassRate 把 `not_recorded` 也计入分母，会错误拉低通过率。
- 应只对 `passed` / `failed` 计分；无 applicable record 时返回 null。
- `GET /api/reports/{report_id}/evaluation` 读取最新 report + feedback 重算；前端在 feedback 保存后重新拉 evaluation，而不必整页刷新。

不能照搬：

- 不把 Pydantic error detail 直接暴露给终端用户。
- 不引入 online evaluation dashboard。

采用结论：

```text
schemaPassRate 只统计 passed/failed；feedback 保存后通过 read API 自动刷新 evaluation。
```

### 3.3 方案对比

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | deterministic metrics + read API refresh | 可解释、可单测、零 LLM judge | 不是完整 RAGAS | **采用** |
| B | RAGAS runtime + LLM-as-judge | 指标更完整 | 超 V3-C 边界，成本高 | 拒绝 |
| C | 单一 report quality score | 实现最简单 | 无法定位 retrieval / grounding 问题 | 拒绝 |

evidence coverage 定义：

| 选项 | 结论 |
| --- | --- |
| insight 只要有任意 evidenceRefs 即算 covered | 拒绝；与 unsupportedInsightCount 冲突 |
| insight 至少绑定一个当前 input evidenceRef 才算 covered | **采用** |

### 3.4 最终方案选择

采用：

```text
deterministic / heuristic evaluation service + workflow step + read API + feedback refresh
```

规则：

- `evidenceCoverage`：至少绑定一个当前 input evidenceRef 的 insight 占比。
- `retrievalCoverage`：history / knowledge items 中带 sourceRefs 的占比；无 item 时为 1.0。
- `unsupportedInsightCount`：无 evidenceRefs 或 refs 未绑定当前 input 的 insight 数。
- `feedbackHitRate`：仅统计当前 report insights 的 feedback；无 feedback 时为 null。
- `schemaPassRate`：仅统计 passed/failed workflow schema records；无 applicable record 时为 null。
- workflow snapshot 与 read API refresh 并存。

### 3.5 调研对实现的影响

相对初版实现，调研后调整：

| 项 | 初版 | 调研后 |
| --- | --- | --- |
| evidenceCoverage | 有任意 evidenceRefs 即算 covered | 必须绑定当前 input evidenceRef |
| schemaPassRate | 全部 schema records 计入分母 | 只计 passed/failed；无 applicable record 时为 null |
| feedback 刷新 | 需整页刷新 | feedback 保存后自动重新拉 evaluation API |
| feedbackHitRate 范围 | 已过滤 report insights | 补明确单测 |

代码影响：

- `backend/app/services/report_evaluation.py`
- `backend/app/schemas/report_evaluation.py`
- `backend/app/tests/unit/test_report_evaluation.py`
- `frontend/src/features/report/FeedbackPanel.tsx`
- `frontend/src/pages/ReportDetailPage.tsx`
- `frontend/src/types/aesthetic.ts`

## 4. 实现摘要

- 新增 `ReportEvaluationMetrics` / `ReportEvaluationResponse` schema。
- 新增 `report_evaluation` service 与 `schema_validation_summary` 共享模块。
- 新增 workflow step `compute_report_evaluation`。
- `ReportResponse.evaluationMetrics` 持久化到 `report_json`。
- 新增 `GET /api/reports/{report_id}/evaluation`。
- 前端 `ReportDetailPage` 新增“质量评估”区块，并在 feedback 保存后刷新 evaluation。

## 5. 指标定义

| 指标 | 含义 |
| --- | --- |
| evidenceCoverage | 至少绑定一个当前 input evidenceRef 的 insight 占比 |
| retrievalCoverage | history / knowledge context items 中带 sourceRefs 的占比 |
| unsupportedInsightCount | 无 evidenceRefs 或未绑定当前 input 的 insight 数 |
| feedbackHitRate | 当前 report 相关 feedback 中 very_me / somewhat_me 占比；无反馈时为 null |
| schemaPassRate | workflow 中 passed 的 schema records / (passed + failed)；无 applicable record 时为 null |

## 6. 验收标准

功能：

- 报告详情页展示“质量评估”区块。
- 指标包含 evidence coverage、retrieval coverage、unsupported insights、schema pass rate、feedback hit rate。
- `GET /api/reports/{report_id}/evaluation` 返回 summary 与 metrics。
- 提交 feedback 后无需整页刷新，feedback hit rate 会自动更新。

治理：

- summary / disclaimer 不输出人格、心理、能力诊断式表达。
- evaluation 指标只用于开发期质量观察。

测试：

- 单元测试：`test_report_evaluation.py`
- 集成测试：`test_api_flow.py` 覆盖 evaluation step 与 API

## 7. 权威设计文档更新

本轮已上升：

- `docs/11-模块拆分与接口测试文档.md`：补充 V3-C grounding / schema pass rate 测试说明。
- `docs/13-验证与评估文档.md`：补充 V3-C evidenceCoverage 与 feedback refresh 治理检查。

## 8. 测试记录

```text
2026-06-17（初版）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，39 passed, 3 warnings。

2026-06-17（调研重对齐后）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，46 passed, 3 warnings。
- 调整 evidenceCoverage grounding 规则、schemaPassRate 分母、feedback 后自动刷新 evaluation。
```

## 9. 人工验收

```text
2026-06-17（调研重对齐后，用户人工验收通过）：
- 报告详情页出现“质量评估”区块。
- 指标包含 evidence coverage、retrieval coverage、unsupported insights、schema pass rate、feedback hit rate。
- GET /api/reports/{report_id}/evaluation 返回 summary 与 metrics。
- Developer Debug 中出现 compute_report_evaluation step。
- 提交 feedback 后，feedback hit rate 会自动更新（无需整页刷新）。
```

## 10. 下一步

```text
V3-C 重验收已通过；下一步进入 V3-D Retrieval / RAG Observability。
```
