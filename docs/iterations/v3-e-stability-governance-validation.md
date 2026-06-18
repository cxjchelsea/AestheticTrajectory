# V3-E：Stability And Governance Validation

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V3-E 是 V3 的最后一个功能验收子阶段，不是 V3 final closure / archive gate。

本轮目标：

```text
验收 V3 personalized retrieval、RAG、knowledge context、evaluation 与 observability 是否遵守 evidence-first 与 governance 边界。
```

V3-E 完成后，才允许进入 V3 final closure / archive gate。

## 2. 上游依据

必须引用：

1. `docs/iterations/v3-0-personalized-retrieval-research.md`
2. `docs/iterations/v3-a-personalized-history-retrieval.md`
3. `docs/iterations/v3-b-aesthetic-knowledge-rag.md`
4. `docs/iterations/v3-c-evaluation-metrics-baseline.md`
5. `docs/iterations/v3-d-retrieval-rag-observability.md`
6. `docs/iterations/v2-e-memory-governance-validation.md`
7. `docs/13-验证与评估文档.md`

V3 子阶段顺序：

```text
V3-0 -> V3-A -> V3-B -> V3-C -> V3-D -> V3-E -> V3 final closure / archive
```

## 3. 问题定义

本轮要回答：

```text
V3 是否没有把 RAG 知识当成用户偏好证据，没有让历史检索覆盖当前输入证据，没有生成无 evidence 的高级结论？
```

具体问题：

- insight `evidenceRefs` 是否只绑定当前 report 的 input ids？
- `historyContext` / `knowledgeContext` 是否与 insight evidence 分离？
- knowledge / history context 是否不进入 profile positive evidence？
- `not_me` 历史反馈是否只作为 negative context？
- evaluation 是否能在 workflow 输出中检出 unsupported insights？
- history / knowledge / evaluation 文案是否避免人格、心理、能力诊断式表达？

## 4. 外部调研与方案选择

### 4.1 调研问题

- V3 全链路治理应沿用 V2-E 自动测试模式，还是重新做人工-only 验收？
- RAG faithfulness 在 mock pipeline 下如何落地为可执行检查？
- profile builder 与 retrieval context 的边界应如何测试？

### 4.2 外部调研记录

#### 记录 1：RAG evaluation 必须区分 retrieval 与 generation grounding

来源名称：Evaluation of Retrieval-Augmented Generation: A Survey

来源类型：论文 / RAG evaluation survey

链接或出处：`https://arxiv.org/html/2405.07437v2`

对 V3-E 的启发：

- V3 治理应分别检查 retrieval context 与 generation output 的 grounding。
- unsupported insight count 是 generation grounding 的 proxy。

采用结论：

```text
V3-E 自动检查 insight evidenceRefs 与 evaluation unsupportedInsightCount。
```

#### 记录 2：V2-E 已建立 memory governance 自动验收模式

来源名称：仓库现状 `test_memory_governance_validation.py`

来源类型：内部工程实践

对 V3-E 的启发：

- V3-E 沿用“集中治理测试文件 + workflow 集成断言”模式。
- 不新增 runtime 治理服务，避免过度工程。

采用结论：

```text
新增 test_v3_governance_validation.py，并补强 workflow 集成断言。
```

#### 记录 3：V3-0 版本级验收标准

来源名称：`docs/iterations/v3-0-personalized-retrieval-research.md` §11

对 V3-E 的启发：

- V3-E 必须覆盖版本级 9 条验收标准中与 A–D 相关的治理项。
- archive gate 留给 V3 final closure，不在本子阶段执行。

采用结论：

```text
V3-E 聚焦 A–D 已落地能力的治理自动验收，不提前做 V4 / archive。
```

### 4.3 方案对比

| 方案 | 做法 | 结论 |
| --- | --- | --- |
| A | 新增 `test_v3_governance_validation.py` + 补强 workflow 测试 | **采用** |
| B | 新建 governance runtime middleware | 拒绝，超范围 |
| C | 仅人工 checklist，无自动测试 | 拒绝，无法回归 |

## 5. 本轮边界

包含：

- V3 全链路治理自动测试。
- workflow 第二份报告 history / knowledge / evaluation 稳定性断言。
- profile 与 retrieval context 隔离检查。
- 文档同步。

不包含：

- V3 final archive gate。
- V4 Agent / MCP。
- 新 retrieval / RAG runtime。
- 真实 LLM / ChromaDB runtime。

## 6. 验收标准

V3-E 通过需要满足：

- workflow 输出 insight 的 `evidenceRefs` 只引用当前 input ids。
- 第二份报告可有 history context，但不污染 insight evidence。
- knowledge / history context 不进入 profile positive evidence。
- `not_me` 历史反馈 direction 为 negative。
- workflow 正常路径 `unsupportedInsightCount == 0`。
- history / knowledge / evaluation disclaimer 与 summary 无诊断式表达。
- 后端治理测试全部通过。
- **用户完成下方人工全链路验收。**

## 6.1 人工验收清单

自动测试覆盖的是代码层治理规则；人工验收需在全链路 UI 上确认 V3-A–D 组合后仍成立。

### 测试 1：当前输入证据优先

**操作**：完成第二份及以上分析，打开报告详情。

**检查**：
- 「重点洞察」每条 `evidenceRefs` 只指向**本次上传**的输入，不包含历史 reportId / knowledge docId。
- 「历史参考」「知识参考」与「重点洞察」分区展示，互不混写。

### 测试 2：RAG 知识不进 profile

**操作**：完成至少一份带「知识参考」的报告 → 对某条洞察提交 `very_me` 或 `somewhat_me` 反馈 → 打开「我的画像」。

**检查**：
- 画像正向条目来自**用户反馈**，不是知识库 docId / 知识标题。
- 画像里没有把知识参考包装成“用户偏好”。

### 测试 3：历史否定不进正向偏好

**操作**：对第一份报告的某条洞察提交 `not_me` → 再跑第二份分析（特征有重叠）。

**检查**：
- 「历史参考」里该反馈为 **negative** 方向。
- 第二份报告不会把它写成正向偏好；画像里该解释进入 rejected/negative，而非 stable 正向条目。

### 测试 4：evaluation 与治理指标

**操作**：在报告详情查看「质量评估」。

**检查**：
- `unsupported insight` 为 0（正常路径）。
- `evidence coverage`、`retrieval coverage` 数值合理。
- summary 无人格、心理、能力诊断式表述。

### 测试 5：mock / 边界诚实标记

**操作**：展开 Developer Debug（`npm run dev`）。

**检查**：
- Mock Usage 仍标明 dev-only / mock。
- retrieval trace 在 abstain 时不伪造选中 item。
- 页面未暗示已接入真实 LLM / 外部 RAG 平台。

### 测试 6：文案治理（快速扫读）

**检查**报告页、画像页、历史对比页：
- 无人格诊断、心理评估、命运判断、消费规训式措辞。
- disclaimer 可以写「不是人格诊断」这类**否定**表述，但正文不做断定式诊断。

## 7. AI 生成计划

```text
1. 新增 test_v3_governance_validation.py。
2. 补强 test_analysis_workflow.py 的 V3 断言。
3. 运行后端测试与前端 build。
4. 同步 12 / 13 / 15 文档。
5. V3-E 通过后，等待用户确认再进入 V3 final closure。
```

禁止 AI 自行决定：

- 不提前把 V3 标记为 archived。
- 不新增 V4 runtime。
- 不把 knowledge context 写入 profile。

## 8. 实现记录

实现日期：

```text
2026-06-17
```

新增自动测试：

```text
backend/app/tests/unit/test_v3_governance_validation.py
```

覆盖：

- workflow insight `evidenceRefs` 只绑定当前 input ids。
- 第二份报告 history context 与 insight evidence 分离。
- knowledge / history context 不进入 profile positive evidence。
- `not_me` 历史反馈保持 negative direction。
- workflow 路径 `unsupportedInsightCount == 0`。
- history / knowledge message、summary、note 无诊断式表达。

补强：

```text
backend/app/tests/integration/test_analysis_workflow.py
```

测试记录：

```text
2026-06-17：REPOSITORY_BACKEND=memory python -m pytest app/tests -q → 54 passed, 3 warnings。
```

人工验收：

```text
2026-06-17：用户人工全链路验收通过（含 not_me 反馈后 feedback hit rate=0%、画像治理检查）。
```

## 9. 当前结论

```text
V3-E 自动治理测试与人工全链路验收均已通过。
V3 已归档：docs/archive/v3/。
```
