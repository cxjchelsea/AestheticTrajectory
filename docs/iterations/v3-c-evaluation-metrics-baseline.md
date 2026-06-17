# V3-C：Evaluation Metrics Baseline

当前状态：

```text
implemented / pending_manual_validation
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

## 3. 外部调研与方案选择（补记）

本节为流程补记，原应在实现 V3-C 前完成；记录内容与当前实现一致，待人工验收。

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.1、§6.3、§6.4
能力级：evaluation metrics baseline、retrieval/generation 分层评估
实现级：deterministic metrics、schema pass rate、feedback hit rate、read API 刷新
```

### 3.1 调研问题

- 在 mock / heuristic pipeline 下，哪些 RAG 指标可以先做 deterministic baseline，而不引入 RAGAS runtime？
- evidence coverage 与 unsupported insight count 应如何对应 grounding / faithfulness 思想？
- retrieval coverage 应如何覆盖 V3-A history context 与 V3-B knowledge context？
- schema validation 结果是否应纳入 baseline metrics？
- 用户反馈后，evaluation 应如何刷新而不重跑整条 generation workflow？

### 3.2 外部调研记录

当前状态：

```text
completed（补记）
```

#### 记录 1：RAG 评估必须拆分 retrieval 与 generation

来源名称：Evaluation of Retrieval-Augmented Generation: A Survey

来源类型：论文 / RAG evaluation survey

链接或出处：`https://arxiv.org/html/2405.07437v2`

调研问题：

- 为什么不能只看“报告好不好”一个总分？
- V3-C baseline 至少应覆盖哪些 failure mode？

核心做法：

- RAG evaluation 需要分别看 retrieval quality、answer quality、grounding / faithfulness。
- end-to-end score 无法定位失败来自检索还是生成。
- 还需要关注 unsupported claims、retrieved documents 与最终输出的关系。

对 V3-C 的启发：

- baseline 至少包含 evidence coverage、retrieval coverage、unsupported insight count、schema pass rate。
- history context 与 knowledge context 的 source ref 覆盖率单独计入 retrievalCoverage。
- 不做单一 LLM 质量分；先做可解释、可单测的 deterministic metrics。

不能照搬：

- 不引入完整 RAG benchmark suite。
- 不做 latency / robustness 全量评估。

采用结论：

```text
V3-C 采用分层 deterministic metrics：generation grounding（evidence / unsupported insights）+ retrieval coverage + workflow schema pass rate。
```

#### 记录 2：RAGAS 指标思想的本地化，而非 runtime 接入

来源名称：RAGAS: Automated Evaluation of Retrieval Augmented Generation

来源类型：论文 / RAG evaluation framework

链接或出处：`https://arxiv.org/html/2309.15217v1`

调研问题：

- 没有人工标注 ground truth 时，哪些指标仍可先做？
- faithfulness / context precision 如何映射到审美报告结构？

核心做法：

- RAGAS 提供 reference-free 的 faithfulness、answer relevance、context precision / recall 等思想。
- faithfulness 检查 answer claims 是否被 retrieved context 支持。
- context precision 关注 retrieved context 是否含过多 noise。

对 V3-C 的启发：

- `unsupportedInsightCount` 是本地版 faithfulness proxy：insight 没有 current input evidenceRefs 即计为 unsupported。
- `retrievalCoverage` 是本地版 context precision proxy：history/knowledge items 是否都带 sourceRefs。
- `feedbackHitRate` 作为 user signal 补充，而不是替代 grounding 指标。
- V3-C 明确不做 RAGAS runtime 与 LLM-as-judge。

不能照搬：

- 不调用 RAGAS LLM judge 提取 claims。
- 不做 context recall（缺少人工标注 ground truth）。

采用结论：

```text
V3-C 借鉴 RAGAS 指标思想，实现本地 heuristic：unsupportedInsightCount、retrievalCoverage、feedbackHitRate；不接入 RAGAS runtime。
```

#### 记录 3：claim-level grounding 检查的最小实现

来源名称：RAG evaluation: Expert guide

来源类型：工程实践 / RAG evaluation guide

链接或出处：`https://www.n-ix.com/rag-evaluation/`

调研问题：

- 为什么 insight-level evidence ref 检查比“整份报告打分”更适合 V3-C？
- 高风险场景还需要什么后续能力？

核心做法：

- grounding error 包括 unsupported facts、过度推断、错误合成多个片段。
- 应优先在 sentence / claim level 检查 material claims 是否有 evidence 支持。
- 结构化人工复核仍不可完全省略，但 automatic baseline 可以先抓“无 evidence 的 insight”。

对 V3-C 的启发：

- 每条 insight 至少应绑定 current input 的 evidenceRefs；否则进入 unsupportedInsightCount。
- evaluation service 从 `ReportResponse` 直接计算，不依赖额外 LLM。
- disclaimer 必须说明指标用于开发期质量观察，不是人格/心理判断。

不能照搬：

- 不做通用事实真伪检查器。
- 不做 sentence-level entailment model。

采用结论：

```text
V3-C 以 insight-level evidence binding 作为最小 grounding 检查；unsupportedInsightCount 成为核心治理指标之一。
```

#### 记录 4：schema validation 与 feedback 后刷新

来源名称 1：Pydantic — Validation errors and model validation

来源类型 1：框架文档 / schema validation

链接或出处 1：`https://docs.pydantic.dev/latest/concepts/validation/`

来源名称 2：RAGAS evaluation guide — reference-free vs reference-based split

来源类型 2：工程实践 / eval 设计

链接或出处 2：`https://learnwithparam.com/blog/ragas-evaluation-rag-pipelines-practical-guide`

调研问题：

- workflow 中 schema validation 结果是否应计入 baseline metrics？
- 用户提交 feedback 后，evaluation 是否应重算？

核心做法：

- 结构化 pipeline 应把 schema validation 作为可观测步骤，而不是 silent failure。
- reference-free metrics 适合高频自动评估；user feedback 属于后置信号，可单独刷新。
- 评估 API 与 report snapshot 分离，可避免每次 feedback 重跑 generation workflow。

对 V3-C 的启发：

- 从 `analysis_logs` / schema validation records 汇总 `schemaPassRate`。
- `GET /api/reports/{report_id}/evaluation` 读取最新 report + feedback 重算 metrics。
- `ReportResponse.evaluationMetrics` 仍保存 workflow 完成时刻 snapshot；read API 用于 feedback 后刷新。

不能照搬：

- 不把 Pydantic error detail 直接暴露给终端用户。
- 不引入在线 evaluation dashboard。

采用结论：

```text
V3-C 增加 schemaPassRate 与 evaluation read API；workflow snapshot + feedback 后 refresh 并存。
```

### 3.3 最终方案选择

采用：

```text
deterministic / heuristic evaluation service + workflow step + read API
```

原因：

- 记录 1–3 支持先做可解释 grounding/retrieval baseline，而非 RAGAS runtime。
- 记录 4 支持 schemaPassRate 与 feedback 后 refresh。
- 当前仍是 mock / heuristic pipeline，不适合引入 LLM-as-judge。
- 指标可直接从 report、feedback、analysis logs 计算。
- API 可在用户反馈后刷新 feedback hit rate。

## 4. 实现摘要

- 新增 `ReportEvaluationMetrics` / `ReportEvaluationResponse` schema。
- 新增 `report_evaluation` service 与 `schema_validation_summary` 共享模块。
- 新增 workflow step `compute_report_evaluation`。
- `ReportResponse.evaluationMetrics` 持久化到 `report_json`。
- 新增 `GET /api/reports/{report_id}/evaluation`。
- 前端 `ReportDetailPage` 新增“质量评估”区块。

## 5. 指标定义

| 指标 | 含义 |
| --- | --- |
| evidenceCoverage | 有 evidenceRefs 的 insight 占比 |
| retrievalCoverage | history / knowledge context items 中带 sourceRefs 的占比 |
| unsupportedInsightCount | evidenceRefs 未绑定当前输入的 insight 数 |
| feedbackHitRate | 报告相关 feedback 中 very_me / somewhat_me 占比；无反馈时为 null |
| schemaPassRate | workflow schema validation passed 占比 |

## 6. 测试记录

```text
2026-06-17：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，39 passed, 3 warnings。
- 前端：npm run build，通过。
```

## 7. 人工验收

```text
待用户确认：
- 报告详情页出现“质量评估”区块。
- 指标包含 evidence coverage、retrieval coverage、unsupported insights、schema pass rate、feedback hit rate。
- GET /api/reports/{report_id}/evaluation 返回 summary 与 metrics。
- Developer Debug 中出现 compute_report_evaluation step。
- 提交 feedback 后刷新页面，feedback hit rate 会更新。
```

## 8. 下一步

```text
用户完成 V3-C 人工验收后，进入 V3-D Retrieval / RAG Observability。
```
