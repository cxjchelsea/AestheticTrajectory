# V1-C：报告生成与反馈闭环

当前状态：

```text
planned / research_required
```

创建日期：

```text
2026-06-16
```

## 1. 本轮目标

在 V1-A 特征抽取和 V1-B 相似性分组基础上，让系统生成一份有证据、有不确定性、非玄学化的审美报告，并收集用户反馈。

本轮目标链路：

```text
InputFeature
↓
SimilarityGroup
↓
PossibleInterpretation
↓
Insight
↓
ReportResponse
↓
Feedback
↓
继续复用现有 API 行为
```

## 2. 当前基线

当前已归档状态：

```text
V1-A accepted / archived
V1-B accepted / archived
```

已确认：

- `InputFeature` 已包含 `promptVersion`、`modelName`、feature evidence。
- `SimilarityGroup` 已基于 embedding similarity 和 feature overlap 生成。
- `EmbeddingRecord` metadata 已保存。
- 现有 `MockInterpretationGenerator` 可以生成 possible interpretations 和 insights。
- 现有 `generate_report` 可以生成 `ReportResponse`。
- 现有 feedback API 可以提交反馈。

当前限制：

- possible interpretations 仍是固定 mock，不充分使用 features / similarity groups。
- insights 仍是固定 mock，不充分绑定具体 feature evidence。
- 报告 summary 仍是固定文案。
- feedback 保存后暂不影响画像或后续报告。
- 未持久化真实 PostgreSQL。

## 3. 本轮解决什么问题

本轮解决：

```text
系统能否基于本次输入的特征与相似性分组，生成结构完整、证据可追踪、不做人格诊断的报告，并完成反馈闭环？
```

本轮不解决：

- 历史报告。
- 长期用户画像。
- 反馈影响画像权重。
- RAG。
- Agent。
- MCP。
- 推荐系统。
- PostgreSQL runtime 持久化。

## 4. 必须阅读的文档

只需要阅读以下文档：

1. `docs/04-审美表征体系文档.md`
2. `docs/05-AI分析逻辑文档.md`
3. `docs/06-输出报告模板文档.md`
4. `docs/09-AI Workflow 编排与任务执行文档.md`
5. `docs/10-Prompt Contract 与结构化输出规范.md`
6. `docs/13-验证与评估文档.md`
7. `docs/12-开发任务拆分与里程碑计划.md`
8. `docs/iterations/v1-a-real-feature-extraction.md`
9. `docs/iterations/v1-b-embedding-similarity.md`

不要一次性读取 `03-16` 全量文档。

## 5. 外部调研与方案选择

本节必须在实现 V1-C 代码前完成。

调研要求：

```text
本轮必须进行外部调研，并在本文档中记录。

不能只基于当前代码和通用工程经验直接设计。
不能只写“通用做法”，必须记录具体来源、可借鉴点、不能照搬点、最终采用 / 不采用理由。
```

### 5.1 调研问题

本轮调研只围绕报告生成与反馈闭环：

- 审美分析报告应该如何组织 summary、feature evidence、interpretation 和 insight？
- 如何让每条 insight 都能追溯到 input evidence？
- uncertainty 应该如何表达，才能避免绝对化结论？
- feedback rating 应该如何建模，才能支持后续画像但不提前进入 V2？
- 报告文案如何避免人格诊断、心理评估和玄学表达？
- mock report generator 和未来真实 LLM report generator 应该如何共用 contract？

### 5.2 外部调研记录

当前状态：

```text
待调研
```

调研记录格式：

```text
来源名称：
来源类型：文档 / 论文 / 产品 / 框架 / 博客 / API 文档
链接或出处：
调研问题：
核心做法：
可借鉴点：
不能照搬点：
对 V1-C 的影响：
采用 / 不采用结论：
```

外部调研完成后，需要把本节从 `待调研` 更新为具体记录。

## 6. 系统边界

本轮包含的能力：

- PossibleInterpretation 生成规则。
- Insight 生成规则。
- ReportResponse 对齐。
- evidenceRefs 约束。
- uncertainty 约束。
- disclaimer。
- feedback schema / API 边界确认。

本轮暂缓的能力：

- 反馈影响长期画像。
- 历史报告对比。
- 报告版本管理。
- LLM runtime。

本轮明确不做：

- V2 历史报告。
- V2 轻量画像。
- RAG。
- Agent。
- MCP。
- 推荐系统。

边界原因：

```text
V1-C 只负责本次分析报告与反馈闭环，不负责长期记忆更新。
反馈数据只保存为后续 V2 画像更新的输入，不在本轮改变用户画像。
```

## 7. 设计待确认

外部调研完成后，需要确认：

- Report summary 生成规则。
- PossibleInterpretation 数量和 evidenceRefs 规则。
- Insight 数量、evidenceRefs 和 uncertainty 规则。
- disclaimer 是否统一由 report generator 输出。
- feedback rating 是否沿用当前 schema。
- 前端是否需要展示更细 evidence 或 error state。

## 8. 实现范围

后续待外部调研和设计确认后补充。

## 9. 不允许 AI 自行决定的内容

本轮禁止自行扩大范围：

- 不新增历史报告。
- 不新增长期用户画像。
- 不新增 RAG。
- 不新增 Agent。
- 不新增 MCP。
- 不接入真实 PostgreSQL。
- 不改变现有 API 路径。
- 不让报告输出人格诊断、心理评估或玄学结论。
- 不让反馈直接改变长期画像。

## 10. 预期涉及文件

后端可能涉及：

```text
backend/app/ai/mock/mock_interpretation_generator.py
backend/app/schemas/interpretation.py
backend/app/schemas/report.py
backend/app/schemas/feedback.py
backend/app/workflows/steps/generate_report.py
backend/app/workflows/aesthetic_analysis_v1.py
backend/app/services/feedback_service.py
backend/app/tests/unit/
backend/app/tests/integration/
```

前端可能涉及：

```text
frontend/src/types/aesthetic.ts
frontend/src/features/report/
frontend/src/services/
```

是否修改前端取决于外部调研和设计确认。

## 11. 验收标准

本轮完成需要满足：

- mock workflow 仍可运行。
- `python -m pytest` 通过。
- 前端 `npm run build` 仍通过。
- 报告包含 summary。
- 报告包含 lowLevelFeatures。
- 报告包含 similarityGroups。
- 报告包含 possibleInterpretations。
- 报告包含 insights。
- 每条 insight 有 evidenceRefs。
- 每条 insight 有 uncertainty。
- 用户可以提交反馈。
- 反馈可以被保存。
- 报告不包含人格诊断和玄学表达。

## 12. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如有接口或 schema 变化，更新对应设计文档。

## 13. 下一轮入口

如果本轮通过，下一轮进入：

```text
V1-D：数据持久化与基础日志
```

如果本轮未通过，继续收口：

```text
报告生成
反馈闭环
evidenceRefs
uncertainty
非诊断表达
```
