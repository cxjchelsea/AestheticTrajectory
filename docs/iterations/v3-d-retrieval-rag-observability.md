# V3-D：Retrieval / RAG Observability

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V3-A / V3-B / V3-C 已具备 history context、knowledge context 与 evaluation metrics 的基础上，补全开发期可观测 trace：

```text
workflow 完成 retrieval / context assembly / evaluation
↓
GET /api/analysis-jobs/{job_id}/debug 返回结构化 trace
↓
报告详情页 Developer Debug Panel 展示 retrieval / context / evaluation trace
↓
开发者可回答“为什么选中这些历史/知识参考、评估指标如何得出”
```

## 2. 上游版本决策

引用 `docs/iterations/v3-0-personalized-retrieval-research.md`：

- V3-D 补全 retrieval trace、context assembly trace、prompt / schema / evaluation trace。
- 提供开发者可查看的调试入口。
- 不做外部 SaaS observability 平台强依赖。
- 不做生产级 tracing pipeline 或实时监控 dashboard。

引用 V3-A / V3-B / V3-C 已落地边界：

- history / knowledge context 与当前 input evidence 分离。
- evaluation metrics 已写入 `report_json` 并由 `compute_report_evaluation` step 产出。
- 现有 `analysis_logs` + `GET /analysis-jobs/{id}/debug` 是 V2 横向 debug 基础设施。

## 3. 本轮解决什么问题

本轮解决：

```text
开发者在本地能否追踪一次分析中的 retrieval 选择、context 组装与 evaluation 计算？
```

本轮不解决：

- LangSmith / OpenTelemetry / Langfuse runtime 接入。
- 持久化 step-level detail JSON 到 `analysis_logs`（需 migration，留待后续）。
- 生产监控 dashboard、实时刷新、告警。
- V3-E 全量治理验收。

## 4. 外部调研与方案选择

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.5–6.7
能力级：RAG observability trace shape、debug API 扩展方式
实现级：从 persisted report + workflow logs 组装 trace、前端 dev panel 分区
```

### 4.1 调研问题

- V3-D 应新建独立 observability API，还是扩展既有 debug endpoint？
- trace 应持久化到 `analysis_logs`，还是从 report + logs 在读取时组装？
- retrieval trace 至少需要哪些字段才能定位“为何选中 / 为何 abstain”？
- evaluation trace 与 V3-C metrics 的关系是什么，如何避免重复口径？
- 没有真实 LLM 时，prompt trace 应如何诚实标记？

### 4.2 外部调研记录

#### 记录 1：OpenTelemetry trace / span 模型

来源名称：OpenTelemetry Observability Primer

来源类型：工程规范 / observability

链接或出处：`https://opentelemetry.io/docs/concepts/observability-primer/`

核心做法：

- Trace 描述单次 request 路径；span 描述路径中的步骤。
- 应先定义 instrumentation，再考虑外部 collector。

对 V3-D 的启发：

- 以 workflow step 为 span 边界；retrieval / evaluation 作为独立 span。
- 现有 `analysis_logs` 已覆盖 step status / latency，可映射为 workflow span。
- V3-D 不接入 OTel runtime，只补齐语义化子 trace。

采用结论：

```text
扩展本地 debug trace schema，不引入 OTel SDK。
```

#### 记录 2：RAG 应用应追踪 retrieval → context → generation

来源名称：The AI Engineer's Guide to LLM Observability with OpenTelemetry

来源类型：工程实践 / LLM observability

链接或出处：`https://agenta.ai/blog/the-ai-engineer-s-guide-to-llm-observability-with-opentelemetry`

核心做法：

- RAG trace 应覆盖 query processing、document retrieval、context preparation、LLM call、response formatting。
- 定位错误需区分 irrelevant retrieval、context truncation、prompt misinterpretation。

对 V3-D 的启发：

- V3-D 至少记录 retrieval step 结果、选中 item 的 matchedFeatures / sourceRefs、context assembly 计数、evaluation 指标来源。
- mock pipeline 下 prompt / token trace 标记为 `not_used`，不伪造 LLM 字段。

采用结论：

```text
实现 retrieval + context assembly + evaluation trace；prompt trace 仅保留 schema validation 映射。
```

#### 记录 3：LangSmith 代表成熟 LLM app tracing 形态

来源名称：LangSmith Observability docs

来源类型：平台文档

链接或出处：`https://docs.langchain.com/langsmith/observability-llm-tutorial`

核心做法：

- 平台记录 run tree、inputs/outputs、retrieved documents、evaluator results。
- 适合真实 LLM runtime 与在线评估。

对 V3-D 的启发：

- 字段设计参考 run tree，但 V3-D 只实现本地只读 debug view。
- 不把 LangSmith 作为运行时依赖。

采用结论：

```text
借鉴 run tree 分区展示，不接入 LangSmith。
```

#### 记录 4：现有项目 debug 基础设施

来源名称：仓库现状（V2 Developer Debug Panel + V3 workflow steps）

来源类型：内部工程实践

调研问题：

- 是否已有可复用 debug endpoint 与 dev panel？
- V3-A/B/C 持久化了哪些可追踪事实？

核心做法：

- `GET /api/analysis-jobs/{job_id}/debug` 已返回 workflowTrace、schemaValidation、boundaryWarnings。
- report 已持久化 `historyContext`、`knowledgeContext`、`evaluationMetrics`。
- `compute_report_evaluation` 已作为 workflow step 写入 `analysis_logs`。

对 V3-D 的启发：

- 最优路径是扩展 `AnalysisJobDebugResponse`，在 `get_debug` 时从 report + logs 组装 trace。
- 避免 DB migration，符合 V3-D “最小调试入口”边界。

采用结论：

```text
扩展 debug API 与 Developer Debug Panel，读取时组装 trace。
```

### 4.3 方案对比

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 扩展 debug API，读取时从 report + logs 组装 trace | 无 migration；与 V2 panel 一致；事实来源单一 | 无法回放未选中候选 | **采用** |
| B | `analysis_logs` 增加 `detail_json` 列持久化 step 输出 | 可记录候选集 | 需 migration；与 report 可能重复 | 延后 |
| C | 新建 `/observability` API + 独立前端页 | 边界清晰 | 重复 V2 debug 入口；超 V3-D 范围 | 拒绝 |
| D | 接入 LangSmith / OTel | 成熟生态 | 成本、隐私、mock 期无收益 | 拒绝 |

最终方案：

```text
方案 A：新增 observability_trace service，扩展 AnalysisJobDebugResponse 与 Developer Debug Panel。
```

## 5. 系统边界

包含：

- `RetrievalStepTrace`：personal_history / aesthetic_knowledge 两步的状态、延迟、选中数、abstain 信息。
- `RetrievalItemTrace`：每条选中 item 的 matchedFeatures、sourceRefs、direction。
- `ContextAssemblyTrace`：history / knowledge item 计数与 abstain 状态。
- `EvaluationTrace`：metrics 快照、schema pass rate、step 状态。
- dev-only Developer Debug Panel 新分区。

不包含：

- 外部 observability SaaS。
- 候选集全量 replay（除非后续增加 step detail 持久化）。
- 真实 prompt / token / cost trace（标记 `not_used`）。

## 6. 验收标准

功能：

- 完成分析后，`GET /api/analysis-jobs/{job_id}/debug` 返回 `retrievalTrace`、`retrievalItems`、`contextAssemblyTrace`、`evaluationTrace`。
- 第二份及以后报告，history retrieval trace 显示选中 item 与 matchedFeatures。
- knowledge retrieval trace 显示 docId、sourceRefs。
- evaluation trace 与 report `evaluationMetrics` 一致。

效果：

- 开发者可从 debug panel 区分 history vs knowledge retrieval。
- abstain 时 message 可见，不伪造选中 item。

异常：

- job 无 reportId 时，trace 字段为空或 null，debug 仍返回 workflowTrace。

安全 / 权限：

- debug endpoint 与 panel 保持 dev-only 语义；不暴露给生产用户路径。

文档：

- 本 iteration 文档记录调研、方案、测试与验收状态。
- 更新 `docs/12`、`docs/15`、`README.md`。

权威设计文档：

```text
No authoritative design doc update required.
本轮只扩展 debug response 字段与 dev panel，不改变 07/11 的稳定模块契约。
```

## 7. 架构影响

- 后端：新增 `observability_trace.py`；扩展 `analysis_debug.py`、`analysis_job_service.py`。
- 前端：扩展 `AnalysisJobDebugResponse` 类型与 `DeveloperDebugPanel`。
- 数据库：不涉及。
- Workflow：不新增 step。

## 8. 模块契约

| 模块 | 输入 | 输出 |
| --- | --- | --- |
| `observability_trace.build_debug_traces` | `ReportResponse`, workflow logs, schema records | retrieval/context/evaluation trace 对象 |
| `AnalysisJobService.get_debug` | job_id | 扩展后的 `AnalysisJobDebugResponse` |

## 9. 数据模型

不涉及新表。trace 为读取时组装的视图模型。

## 10. API 设计

扩展既有：

```text
GET /api/analysis-jobs/{job_id}/debug
```

新增响应字段：

- `retrievalTrace`
- `retrievalItems`
- `contextAssemblyTrace`
- `evaluationTrace`

## 11. Prompt / Skill / Workflow

不涉及新 prompt。`schemaValidation` 继续作为 prompt/schema 边界 trace 的代理。

## 12. 测试计划

- 单元测试：`test_observability_trace.py` 覆盖 abstain、选中 item、evaluation 对齐。
- 集成测试：`test_api_flow.py` 断言 debug 新字段存在且合理。
- 前端：`npm run build` 通过。

## 13. 实现记录

实现日期：

```text
2026-06-17
```

后端：

- 新增 `backend/app/services/observability_trace.py`：`build_debug_traces` 从 report + workflow logs 组装 trace。
- 扩展 `backend/app/schemas/analysis_debug.py`：`RetrievalStepTrace`、`RetrievalItemTrace`、`ContextAssemblyTrace`、`EvaluationTrace`。
- 扩展 `AnalysisJobService.get_debug`：加载 report 并填充新 trace 字段。

前端：

- 扩展 `AnalysisJobDebugResponse` 类型。
- `DeveloperDebugPanel` 新增 Retrieval Trace / Retrieval Items / Context Assembly / Evaluation Trace 分区。

测试：

```text
2026-06-17：REPOSITORY_BACKEND=memory python -m pytest app/tests -q → 48 passed；frontend build passed。
2026-06-17：REPOSITORY_BACKEND=database python -m pytest app/tests/unit/test_database_repositories.py app/tests/integration/test_api_flow.py -q → 6 passed。
```

人工验收：

```text
2026-06-17：用户人工验收通过。
```

## 14. 当前结论

```text
V3-D 已实现 retrieval / context / evaluation observability trace，并接入 Developer Debug Panel。
人工验收已通过；下一步进入 V3-E Stability And Governance Validation。
```
