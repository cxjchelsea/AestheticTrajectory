# V3-0：Personalized Retrieval / RAG / Evaluation 版本级调研与架构拆分

当前状态：

```text
ready_for_review / no_runtime_implementation
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V3-0 是 V3 的版本级研究与架构闸门，不是功能实现阶段。

本轮目标：

```text
在 V2 Memory / User Model baseline 之上，明确 V3 personalized retrieval、RAG、evaluation 和 observability 的能力地图、边界、数据/API/Workflow 影响、子阶段拆分与验收标准。
```

为什么必须先做这一轮：

```text
V3 涉及检索、知识增强、评估和可观测性，如果直接进入实现，容易把 RAG 知识误写成用户偏好证据，或把 observability 工具接入变成早期过度工程。

V3-0 的职责是先区分：什么是用户历史证据，什么是外部知识，什么是评估记录，什么是运行时 trace；并明确 V3 哪些子阶段可以先做轻量实现，哪些必须延后。
```

## 2. 上游依据

必须引用：

1. `docs/01-产品概念说明书.md`
2. `docs/02-版本迭代路线图.md`
3. `docs/07-数据结构与系统架构文档.md`
4. `docs/11-模块拆分与接口测试文档.md`
5. `docs/12-开发任务拆分与里程碑计划.md`
6. `docs/13-验证与评估文档.md`
7. `docs/15-迭代执行记录.md`
8. `docs/archive/v2/V2-归档说明.md`
9. `docs/archive/v2/V2-任务拆分与里程碑计划.md`
10. `.cursor/skills/project-development-flow/SKILL.md`

## 3. 对应的 Agent 前沿方向

V3 主要推进：

```text
Personalized Retrieval
RAG for Explanation
Evaluation / Observability
Preference Explanation
Memory / User Model Governance
```

V3 不进入：

```text
Agent Runtime
MCP 外部上下文接入
知识图谱 runtime
音乐 / 视频多模态扩展
主动长期观察
```

## 4. 版本核心问题

V3 要回答：

```text
报告是否能参考历史和审美知识，同时仍然保持证据可追踪、评价可量化、失败可诊断？
```

拆成更具体的问题：

```text
历史检索结果如何作为解释上下文，而不是直接变成偏好结论？
外部审美知识如何帮助解释风格概念，而不是覆盖用户输入证据？
每条洞察如何标明来自当前输入、历史证据、用户反馈还是外部知识？
系统如何评估 retrieval 是否有用、RAG 是否忠实、报告是否仍有 evidence？
出现错误解释时，开发者如何追踪是 retrieval、prompt、schema、LLM 还是 UI 表达出了问题？
```

## 5. 本轮调研问题

版本级调研：

- Personalized retrieval 在用户偏好系统中应该检索哪些对象？
- RAG 应该用于解释增强，还是用于生成用户偏好结论？
- RAG 系统的评估应拆成哪些维度？
- LLM / RAG observability 应记录哪些 trace、metrics 和 logs？
- V3 如何继承 V2 的 evidence-first、feedback governance 和 non-diagnostic expression？

能力级调研：

- 检索对象是 raw inputs、features、reports、profile items、feedback，还是外部 knowledge chunks？
- 检索结果是否需要单独的 evidence type？
- evaluation records 是否应该持久化？
- retrieval trace 是否进入业务数据库，还是先进入 analysis/debug logs？
- 评估指标如何从当前已有数据中轻量计算？

实现级调研：

- 当前 `aesthetic_reports.report_json`、`profile_evidence`、`analysis_logs` 是否足够支撑 V3-A？
- 是否需要启用 ChromaDB runtime，还是先用 PostgreSQL / heuristic retrieval 验证边界？
- 前端是否先展示“历史参考说明”，还是先做开发者 evaluation panel？
- 是否需要接入 LangSmith / OpenTelemetry，还是先保留本地 trace 结构？

## 6. 外部调研记录

### 6.1 RAG 评估需要拆分 retrieval、generation 和 grounding

来源名称：Evaluation of Retrieval-Augmented Generation: A Survey

来源类型：论文 / RAG evaluation survey

链接或出处：`https://arxiv.org/html/2405.07437v2`

调研问题：

- RAG 系统是否只看最终回答质量即可？
- 如何定位 RAG 失败来自检索还是生成？

核心做法：

- RAG evaluation 不应只有 end-to-end score。
- 需要分开评估 retrieval quality、answer quality、grounding / faithfulness。
- RAG 还需要考虑 noisy documents、latency、robustness、hallucination 和 retrieved documents 与最终答案的关系。

对 V3 的启发：

- V3 的 evaluation 不能只记录“报告好不好”，至少要拆成 retrieval coverage、evidence coverage、faithfulness / unsupported claim、用户反馈命中。
- 最近报告、profile evidence 和外部 knowledge chunks 都需要被分开追踪来源。

采用结论：

```text
V3 采用分层评估：retrieval -> grounding -> report quality -> user feedback。
V3-A 不追求完整 RAG benchmark，先记录可解释 trace 和最小指标。
```

### 6.2 RAG grounding / citation 是控制幻觉的核心

来源名称：Retrieval-Augmented Generation for Natural Language Processing: A Survey

来源类型：论文 / RAG survey

链接或出处：`https://arxiv.org/pdf/2407.13193`

调研问题：

- RAG 如何减少 hallucination？
- citation / grounding 在 V3 中应该如何体现？

核心做法：

- RAG 通过外部知识库提供可验证上下文，降低依赖模型参数记忆。
- 对需要可控输出的应用，citation、abstention、answer-only-from-information 等机制很重要。
- 外部知识更新可以降低知识过时问题，但也引入 source control 和 grounding 问题。

对 V3 的启发：

- 审美知识库只能作为解释背景，不是用户偏好事实。
- 如果报告使用外部知识，必须显示 knowledge source refs。
- 当没有足够当前输入或历史证据时，应保留不确定表达，而不是靠知识库补高级结论。

采用结论：

```text
V3 RAG 的定位是 explanation support，不是 preference evidence。
报告中必须区分 input evidence、history evidence、profile evidence、knowledge evidence。
```

### 6.3 RAGAS 的核心指标适合作为 V3 最小评估参考

来源名称：RAGAS: Automated Evaluation of Retrieval Augmented Generation

来源类型：论文 / RAG evaluation framework

链接或出处：`https://arxiv.org/html/2309.15217v1`

调研问题：

- 没有大量人工标注数据时，如何评估 RAG？
- 哪些指标适合进入 V3 最小 evaluation？

核心做法：

- RAGAS 聚焦 reference-free evaluation。
- 常见指标包括 faithfulness、answer relevance、context relevance / precision、context recall。
- Faithfulness 关注回答是否由检索上下文支持。
- Context relevance 关注检索上下文是否包含太多噪声。

对 V3 的启发：

- V3 可以借鉴 faithfulness、context precision、context recall 的思想，但不必立即接入完整 RAGAS runtime。
- 对审美报告来说，可先做本地轻量指标：retrieved item count、used evidence count、unsupported insight count、feedback hit rate。

采用结论：

```text
V3-0 只记录指标设计；V3-A / V3-B 再决定是否实现 RAGAS-style 自动评估。
```

### 6.4 RAG 失败需要 claim-level / evidence-level 检查

来源名称：RAG evaluation: Expert guide

来源类型：工程实践 / RAG evaluation guide

链接或出处：`https://www.n-ix.com/rag-evaluation/`

调研问题：

- 为什么整体评分不够？
- 如何发现 unsupported claim？

核心做法：

- RAG grounding error 包括 unsupported facts、过度推断、错误合成多个片段。
- 需要在 sentence 或 claim level 检查 material claims 是否被 retrieved evidence 支持。
- 高风险场景仍需要结构化人工复核。

对 V3 的启发：

- 审美报告中的每条 insight 至少要保留 evidence refs。
- 如果 insight 使用历史或知识增强，必须能追踪到具体 history / knowledge ref。
- V3 的 hallucination check 应先聚焦“洞察是否无 evidence”而不是通用事实真伪。

采用结论：

```text
V3 evaluation 优先检查 unsupported insight / unsupported interpretation，不做泛化事实检查器。
```

### 6.5 OpenTelemetry 的 traces / metrics / logs 可作为长期 observability 方向

来源名称：OpenTelemetry Observability Primer

来源类型：工程规范 / observability

链接或出处：`https://opentelemetry.io/docs/concepts/observability-primer/`

调研问题：

- V3 是否要立刻接入 OpenTelemetry？
- observability 的基本对象是什么？

核心做法：

- Observability 依靠 traces、metrics、logs。
- Trace 记录单个 request 的路径，span 记录其中的步骤。
- Proper instrumentation 的目标是让开发者无需额外临时加日志即可定位问题。

对 V3 的启发：

- V3 的 retrieval / RAG / evaluation pipeline 应先定义 trace schema。
- 现有 `analysis_logs` 可以继续承接最小 trace，不必马上接入 OTel Collector。
- 外部 observability runtime 可在 V3 后续子阶段评估。

采用结论：

```text
V3-0 定义 trace shape；V3-A 仍可使用本地 analysis/debug logs；OpenTelemetry runtime 暂不接入。
```

### 6.6 LLM observability 需要完整追踪 retrieval、prompt 和 LLM 调用

来源名称：The AI Engineer's Guide to LLM Observability with OpenTelemetry

来源类型：工程实践 / LLM observability

链接或出处：`https://agenta.ai/blog/the-ai-engineer-s-guide-to-llm-observability-with-opentelemetry`

调研问题：

- RAG 应用具体应该追踪哪些步骤？
- 出错时如何定位 retrieval、prompt 或 LLM 责任？

核心做法：

- 对 RAG 应用，trace 应覆盖 query processing、document retrieval、context preparation、LLM call、response formatting。
- Trace 中应保留 retrieval query、returned documents、prompt、response、token usage、cost、latency。
- 错误答案常常需要从 retrieval irrelevant、context truncation、prompt misinterpretation 等维度定位。

对 V3 的启发：

- V3 的 workflow trace 需要新增 retrieval trace、prompt context trace、evaluation trace。
- token / cost 只有接入真实 LLM 后才记录；V3-0 只定义字段。

采用结论：

```text
V3 子阶段应先实现可解释 trace，再接外部 observability 平台。
```

### 6.7 LangSmith 代表 LLM app tracing + evaluation 的成熟形态

来源名称：LangSmith Observability / LangSmith tracing docs

来源类型：平台文档 / LLM observability and evaluation

链接或出处：

- `https://langchain.com/langsmith`
- `https://docs.langchain.com/langsmith/observability-llm-tutorial`

调研问题：

- LLM app observability 平台通常记录哪些信息？
- V3 是否应该直接接入 LangSmith？

核心做法：

- LangSmith 提供 end-to-end traces，记录 inputs、outputs、tool calls、latency、metadata。
- 支持 offline evaluation、online evaluation、dataset、human annotation、dashboard。
- 对 RAG pipeline，可观察 retrieval 到 generation 的完整链路。

对 V3 的启发：

- V3 需要 versioned evaluation records 和 trace metadata 的概念。
- 但直接接入 SaaS observability 平台会引入配置、成本、隐私和供应商依赖。

采用结论：

```text
V3-0 不接入 LangSmith runtime；只借鉴 trace / evaluation dataset / online-offline eval 的概念。
```

## 7. V3 能力地图

### 7.1 Personalized Retrieval

目标：

```text
从用户历史输入、历史报告、profile evidence 和反馈中检索与当前输入相关的上下文，用于辅助解释。
```

候选检索对象：

- 历史输入摘要。
- 历史报告 summary / insights。
- profile items。
- profile evidence。
- 用户认可 / 否定的 interpretations。
- 最近两次报告对比结果。

关键规则：

- 历史检索结果是 `history_context`，不是新的当前输入证据。
- 被用户否定的解释可以作为 negative context，但不能作为正向偏好。
- 检索结果必须保留 source refs。

### 7.2 RAG For Explanation

目标：

```text
使用小型审美知识库解释风格概念、视觉语言和文本意象，但不替用户生成无证据偏好结论。
```

候选知识对象：

- 风格概念解释。
- 色彩 / 构图 / 材质 / 空间 / 文学意象基础知识。
- 项目自有审美表征说明。
- 报告写作约束和禁止表达。

关键规则：

- 知识库只提供 explanatory context。
- 知识 evidence 不能替代 input evidence。
- 报告必须区分“当前输入观察”和“外部知识解释”。

### 7.3 Evaluation

目标：

```text
把 V1/V2 的 schema / evidence / feedback 验收扩展为 V3 的 retrieval 和 RAG 质量评估。
```

候选指标：

- evidence coverage：有 evidence refs 的 insight 比例。
- retrieval coverage：报告使用的 history / knowledge context 是否有 refs。
- context precision：检索结果中真正被报告使用的比例。
- unsupported insight count：没有当前输入、历史或知识证据支持的 insight 数。
- feedback hit rate：用户认可的 insight 占比。
- grouping stability：相似输入在不同 run 中的分组稳定性。
- schema pass rate：LLM / report output schema 校验通过率。

### 7.4 Observability

目标：

```text
让每次分析任务能追踪 retrieval、context assembly、generation、evaluation 和 fallback / warning。
```

最小 trace：

- request / job id。
- input ids。
- retrieval query。
- retrieved history refs。
- retrieved knowledge refs。
- selected context refs。
- prompt version。
- model name。
- generation status。
- schema validation result。
- evaluation metrics。
- fallback / boundary warnings。

### 7.5 Governance

V3 必须继承 V2 的治理规则：

- 先 evidence，后 profile。
- 当前输入证据优先于历史检索。
- 用户反馈优先于模型解释。
- 外部知识不得写成用户偏好。
- 不输出人格诊断、心理评估、命运判断或消费规训。
- 被否定解释不得复现为正向画像。
- 无 evidence 的高级词不得进入洞察结论。

## 8. V3 架构边界

### 8.1 数据边界

V3 可能新增：

- retrieval records。
- knowledge chunks。
- knowledge sources。
- evaluation records。
- retrieval trace / context assembly trace。

V3-0 不决定最终表结构，只提出候选对象。具体表结构应在 V3-A / V3-B 实现前写入 `docs/07-数据结构与系统架构文档.md`。

### 8.2 API 边界

V3 可能新增：

- 查询当前报告的 retrieval trace。
- 查询 evaluation summary。
- 查询 knowledge source refs。
- 开发环境下查看 RAG / retrieval debug。

V3-0 不定义最终 API path。具体 API contract 应在对应实现子阶段写入 `docs/11-模块拆分与接口测试文档.md`。

### 8.3 Workflow 边界

V3 可能把 report workflow 扩展为：

```text
loadInputs
extractLowLevelFeatures
generateEmbeddings
groupInputsBySimilarity
retrievePersonalHistory
retrieveAestheticKnowledge
assembleEvidenceContext
generatePossibleInterpretations
generateReport
evaluateReportGrounding
saveReportAndTrace
collectFeedback
```

V3-0 不实现这些 step，只确定方向。

### 8.4 Frontend 边界

V3 可能新增：

- 报告中的历史参考说明。
- 报告中的知识来源说明。
- 开发者 evaluation / retrieval trace 面板。
- 简单评估摘要。

V3 不应在用户侧展示复杂 dashboard。

## 9. 方案取舍

### 9.1 Personalized Retrieval 先于完整知识库 RAG

采用：

```text
先做用户历史检索，再做外部知识库 RAG。
```

原因：

- V2 已经有 reports、profile evidence、feedback，历史检索有数据基础。
- 外部知识库需要额外知识 chunk、source、更新和治理，不应先于用户证据。
- 产品核心是审美演化，不是百科式风格解释。

### 9.2 先记录 trace，再接外部 observability 平台

采用：

```text
先扩展本地 analysis/debug trace，暂不接 LangSmith / OpenTelemetry runtime。
```

原因：

- 当前项目仍是本地开发和作品集验证阶段。
- 外部平台会引入账号、成本、隐私和配置复杂度。
- V3 的首要目标是定义 trace shape 和可诊断边界。

### 9.3 先做轻量指标，再做 LLM-as-judge

采用：

```text
先做 deterministic / heuristic evaluation，再评估 RAGAS-style LLM-as-judge。
```

原因：

- 当前还没有真实 LLM runtime。
- LLM-as-judge 本身有不稳定性，需要 prompt、模型和成本控制。
- evidence coverage、unsupported insight count、schema pass rate 可以先用结构化数据计算。

### 9.4 外部知识只做解释，不做偏好证据

采用：

```text
knowledge evidence 只能支持风格概念解释，不能写入 profile item 的正向偏好证据。
```

原因：

- 用户偏好必须来自用户输入、报告洞察和反馈。
- 外部知识可能提高表达质量，但不能证明用户喜欢某种风格。

## 10. V3 子阶段拆分

建议 V3 拆分为：

### V3-0：版本级研究与架构拆分

状态：

```text
ready_for_review / no_runtime_implementation
```

范围：

- 版本级外部调研。
- 能力地图。
- 架构边界。
- 子阶段拆分。
- 验收标准。

### V3-A：Personalized History Retrieval

目标：

```text
基于 V2 reports / profile evidence / feedback 构建最小历史检索上下文，并在报告生成或报告详情中可追溯展示。
```

不做：

- 外部知识库 RAG。
- LangSmith / OpenTelemetry runtime。
- 长期 Agent。

### V3-B：Aesthetic Knowledge RAG

目标：

```text
引入小型审美知识库，用于解释风格概念和视觉 / 文本意象，并保留 source refs。
```

不做：

- 把知识库内容写入用户画像。
- 大规模知识库。
- 知识图谱。

### V3-C：Evaluation Metrics Baseline

目标：

```text
实现 evidence coverage、retrieval coverage、unsupported insight count、feedback hit rate、schema pass rate 等最小评估指标。
```

不做：

- 完整 RAGAS runtime。
- 在线 LLM-as-judge。
- 复杂评估 dashboard。

### V3-D：Retrieval / RAG Observability

目标：

```text
补全 retrieval trace、context assembly trace、prompt / schema / evaluation trace，并提供开发者可查看的调试入口。
```

不做：

- 外部 SaaS observability 平台强依赖。
- 生产级 tracing pipeline。
- 实时监控 dashboard。

### V3-E：V3 Stability And Governance Validation

目标：

```text
验证 V3 不把 RAG 知识当成用户偏好证据，不让历史检索覆盖当前输入证据，不生成无 evidence 的高级结论。
```

不做：

- V4 Agent / MCP。
- 主动长期观察。

## 11. V3 版本级验收标准

V3 完成时必须满足：

- 报告可以引用历史记录，但当前输入证据仍然优先。
- 外部知识有 source refs。
- 每条增强洞察能追踪到 input / history / profile / feedback / knowledge refs。
- RAG 知识不进入正向 profile evidence。
- evaluation summary 至少包含 evidence coverage、retrieval coverage、unsupported insight count、schema pass rate。
- retrieval / generation / evaluation trace 可在开发环境查看。
- 页面不输出人格诊断、心理评估、命运判断或消费规训。
- fallback / mock / unavailable retrieval 必须显式标记。
- V3 结束前有 archive gate 和 legacy issue audit。

## 12. 需要上升到权威设计文档的决策

V3-0 ready_for_review 后，建议将以下长期决策上升到权威设计文档：

- `docs/07-数据结构与系统架构文档.md`：新增 V3 候选数据对象和 evidence source 边界。
- `docs/11-模块拆分与接口测试文档.md`：新增 retrieval、knowledge RAG、evaluation、observability 模块边界。
- `docs/13-验证与评估文档.md`：新增 V3 evaluation metrics 和 governance checks。
- `docs/12-开发任务拆分与里程碑计划.md`：确认 V3-A 作为下一实现子阶段。

本轮暂不直接修改 07 / 11 / 13 的稳定设计正文，避免在方案未复核前把候选架构写成正式实现契约。

## 13. 当前结论

```text
V3-0 版本级研究与架构拆分已建立。
V3 应先从 personalized history retrieval 开始，而不是直接做完整 RAG runtime。
V3-A 的建议方向是：Personalized History Retrieval。
进入 V3-A 前，需要确认是否接受本文件的子阶段拆分和设计上升目标。
```
