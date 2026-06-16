# V1-C：报告生成与反馈闭环

当前状态：

```text
accepted / archived
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
completed
```

#### 记录 1：OpenAI Structured Outputs

来源名称：OpenAI Structured Outputs

来源类型：API 文档

链接或出处：`https://developers.openai.com/api/docs/guides/structured-outputs`

调研问题：

- 未来真实 LLM report generator 如何保证输出结构稳定？
- schema 约束能否防止 hallucination？

核心做法：

- Structured Outputs 使用 JSON Schema 和 strict mode，让模型输出符合开发者定义的结构。
- 相比 JSON mode，Structured Outputs 不只是保证 JSON 合法，还保证字段符合 schema。
- 文档也明确：结构符合 schema 不等于事实不 hallucinate；如果上下文不足，模型仍可能为了填字段而编造内容。
- 模型拒绝时可能返回 refusal，而不是符合业务 schema 的对象。

可借鉴点：

- V1-C 的 mock report generator 和未来 LLM report generator 应共用结构化 schema。
- report / interpretation / insight 必须先通过 schema validator，再进入 API response。
- schema 中需要保留 uncertainty / evidenceRefs，不要只强制填“结论”。

不能照搬点：

- 本轮不接真实 OpenAI runtime。
- 不能以为 schema compliance 等于内容 grounded。
- 不为了填满 schema 而强行生成解释。

对 V1-C 的影响：

- 报告生成需要继续保持 Pydantic schema contract。
- 后续真实 LLM 接入时，应设置 refusal / insufficient_evidence 逃生路径。

采用 / 不采用结论：

- 采用结构化输出和 schema-first 思路。
- 本轮不采用 OpenAI runtime。

#### 记录 2：Google PAIR Explainability + Trust

来源名称：Google People + AI Guidebook - Explainability + Trust

来源类型：产品设计指南

链接或出处：`https://pair.withgoogle.com/chapter/People%20+%20AI%20Guidebook%20-%20Explainability%20+%20Trust.pdf`

调研问题：

- AI 报告应该如何表达解释和不确定性？
- 如何避免用户过度相信系统输出？

核心做法：

- AI 系统基于概率和不确定性，解释的目的不是暴露全部内部细节，而是帮助用户校准信任。
- 需要帮助用户理解系统能力、限制，以及何时应该应用自己的判断。
- confidence / uncertainty 的展示会影响用户决策，应该谨慎设计。

可借鉴点：

- V1-C report disclaimer 不能只是尾部形式化文案，而要贯穿 summary、interpretation 和 insight。
- insight 应明确“系统观察到什么”和“可能解释什么”。
- uncertainty 应用自然语言说明样本数量、mock 边界和解释候选性质。

不能照搬点：

- 本轮不做复杂 confidence visualization。
- 不把 confidence 百分比包装成精确可靠度。

对 V1-C 的影响：

- 每条 insight 必须有 uncertainty。
- summary 使用“在这组样本中”“可能”“倾向于”等倾向性表达。

采用 / 不采用结论：

- 采用 trust calibration 和 plain-language uncertainty。
- 不采用复杂置信度 UI。

#### 记录 3：Microsoft Responsible AI Standard / Transparency Notes

来源名称：Microsoft Responsible AI Standard and Azure OpenAI Transparency Note

来源类型：Responsible AI 文档

链接或出处：

- `https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Microsoft-Responsible-AI-Standard-General-Requirements.pdf`
- `https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/transparency-note`

调研问题：

- 报告生成系统应该如何说明能力和限制？
- 如何降低 automation bias？

核心做法：

- AI 系统需要支持 stakeholder 理解系统用途、行为和限制。
- 透明度材料应说明 intended uses、limitations、适用范围和不能用于哪些场景。
- 对生成式 AI，需要说明输出可能不准确或误导，并保留 human-in-the-loop。

可借鉴点：

- V1-C report disclaimer 应明确：报告是当前输入的审美观察，不是人格诊断、心理评估或长期画像。
- feedback 应作为用户校正渠道，而不是系统自动认定真相。
- V1-C 文档需保留不适用范围。

不能照搬点：

- 本轮不写完整 Transparency Note。
- 不接企业级审计或治理平台。

对 V1-C 的影响：

- 报告中必须保留 disclaimer。
- feedback 保存后不直接改变画像，避免未经确认的 automation bias。

采用 / 不采用结论：

- 采用透明度和 human-in-the-loop 原则。
- 不采用完整企业治理流程。

#### 记录 4：Nielsen Norman Group - AI Summaries / Error Checking

来源名称：Nielsen Norman Group AI summaries and error checking articles

来源类型：UX 研究文章

链接或出处：

- `https://www.nngroup.com/articles/ai-reviews/`
- `https://www.nngroup.com/articles/ai-chatbots-discourage-error-checking/`

调研问题：

- AI summary 如何建立信任？
- 仅靠 disclaimer 是否足够？

核心做法：

- AI summaries 应连接到实际来源，通过 counts、quotes、links 或 source snippets 帮助用户核查。
- 生成式 AI 容易以自信语气输出错误，界面应让 error checking 更容易。
- AI summary 应补充原始材料，而不是替代原始材料。

可借鉴点：

- V1-C 每条 insight 必须保留 `evidenceRefs`。
- report 页面应能让用户看到 insight 对应的输入证据。
- 报告生成不应只给漂亮总结，还要保留可追踪证据。

不能照搬点：

- 本轮不是电商评论总结，不需要 positive / negative review themes。
- 本轮不做复杂来源链接 UI。

对 V1-C 的影响：

- evidenceRefs 是 V1-C 的硬约束。
- summary 只做概览，不能替代 lowLevelFeatures 和 similarityGroups。

采用 / 不采用结论：

- 采用 evidence-first report。
- 不采用复杂 source browsing UI。

#### 记录 5：Grounded Generation / Citation Architecture

来源名称：Citation-aware RAG / grounded attribution references

来源类型：工程文章 / 论文

链接或出处：

- `https://www.buzzi.ai/insights/ai-document-retrieval-rag-citation-architecture`
- `https://aclanthology.org/2024.konvens-main.6.pdf`
- `https://arxiv.org/pdf/2409.11242`

调研问题：

- 生成文本如何绑定 evidence？
- 如何处理证据不足？

核心做法：

- 每个 material claim 应映射到一个或多个证据来源。
- citations / attributions 应使用稳定 ID。
- 若上下文不足，应 abstain、重新检索或明确说明不能支持该结论。
- 评估可关注 citation precision、citation recall 和 groundedness。

可借鉴点：

- V1-C 的 `evidenceRefs` 应引用 input id，而不是自由文本。
- insight 只能基于已有 features / groups / interpretations 生成。
- 没有足够 evidence 时，应降低 confidence 或不生成该 insight。

不能照搬点：

- 本轮不做 RAG。
- 不引入 citation precision/recall 自动评估。
- 不做外部知识引用。

对 V1-C 的影响：

- `evidenceRefs` 必须是稳定 input id。
- mock generator 也不能输出无证据 insight。

采用 / 不采用结论：

- 采用 claim-to-evidence mapping。
- 不采用 RAG runtime 和 citation evaluator。

#### 记录 6：LangSmith / MLflow Human Feedback

来源名称：LangSmith feedback docs / MLflow GenAI human feedback

来源类型：观测与评估框架文档

链接或出处：

- `https://docs.langchain.com/langsmith/attach-user-feedback`
- `https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/human-feedback`

调研问题：

- 用户反馈应该如何记录，才能后续用于评估或优化？
- feedback 是否应该绑定到具体 insight / run？

核心做法：

- LangSmith 支持把 feedback 绑定到 trace 或具体 run。
- feedback 可包含 key、score、comment、correction 等结构。
- MLflow 示例中，用户可通过 thumbs up/down 给输出反馈，并保留 rationale。
- 生产系统通常把反馈 UI 事件记录到后端，再用于评估和改进。

可借鉴点：

- V1-C 当前 `InsightFeedbackResponse` 绑定 `insightId` 是合理方向。
- feedback 应包含 rating 和 comment。
- 后续 V2 / V3 可把 feedback 作为画像和评估输入。

不能照搬点：

- 本轮不接 LangSmith / MLflow。
- 本轮不做 trace id 或 run id 观测体系。
- 本轮不让 feedback 自动改画像。

对 V1-C 的影响：

- 沿用当前 feedback schema，不扩张。
- 可在文档中明确 feedback 是后续画像输入，不在本轮即时生效。

采用 / 不采用结论：

- 采用 insight-level structured feedback。
- 不采用外部 observability runtime。

#### 记录 7：Guidelines for Human-AI Interaction

来源名称：Guidelines for Human-AI Interaction, Amershi et al. 2019

来源类型：HCI 论文 / 设计指南

链接或出处：

- `https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/publications/`
- `https://dl.acm.org/doi/fullHtml/10.1145/3290605.3300233`

调研问题：

- AI 系统在不确定时应该如何表现？
- 用户反馈应该是全局设置还是单次输出反馈？

核心做法：

- Guideline 10：不确定时缩小服务范围或请求澄清。
- Guideline 15：鼓励 granular feedback，即用户可对具体 AI 输出给反馈。
- Guideline 17：global controls 与 granular feedback 不同。

可借鉴点：

- V1-C feedback 应继续绑定具体 insight，而不是全局画像设置。
- 当 evidence 不足时，报告生成应减少结论数量或输出 uncertainty，而不是强行解释。

不能照搬点：

- 本轮不做全局控制面板。
- 本轮不做复杂 AI 行为自适应。

对 V1-C 的影响：

- feedback schema 保持 insight-level。
- 不确定时减少生成或降低 confidence。

采用 / 不采用结论：

- 采用 granular feedback。
- 不采用 global controls。

### 5.3 调研结论与可借鉴模式

本轮可采用：

- schema-first report / interpretation / insight 生成。
- claim-to-evidence mapping：每条 insight 必须有 `evidenceRefs`。
- plain-language uncertainty：每条 insight 和 interpretation 都要说明不确定性。
- report summary 只做概览，不替代 feature / group / evidence。
- feedback 绑定具体 insight，保留 rating 和 comment。
- disclaimer 明确报告不是人格诊断、心理评估或长期画像。
- evidence 不足时减少结论或降低 confidence，而不是编造。

本轮不采用：

- 真实 LLM runtime。
- OpenAI Structured Outputs runtime。
- RAG / 外部知识 citations。
- citation precision / recall 自动评估。
- LangSmith / MLflow runtime。
- feedback 直接改变长期画像。
- 全局用户画像控制面板。

### 5.4 本轮采用方案

外部调研后采用：

```text
ReportGenerator / InterpretationGenerator 继续保留 mock 边界
基于 InputFeature + SimilarityGroup 生成 summary
PossibleInterpretation 绑定 input-level evidenceRefs
Insight 绑定 input-level evidenceRefs
每条 interpretation / insight 都有 uncertainty
feedback schema 暂时沿用 rating + comment
feedback 只保存，不更新画像
disclaimer 统一输出
```

设计确认结果：

- report summary 生成规则已确认。
- possible interpretations 数量和 evidenceRefs 规则已确认。
- insights 数量、evidenceRefs 和 uncertainty 规则已确认。
- confidence 默认值和降低规则已确认。
- feedback schema 维持不变。
- 前端本轮不新增复杂 evidence UI，只复用现有 InsightCard 和 FeedbackPanel。

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

## 7. 设计确认

当前状态：

```text
confirmed
```

本节把外部调研结论落成 V1-C 可执行设计。完成本节后，V1-C 可以进入代码实现。

### 7.1 Report Summary 生成规则

输入来源：

- `InputFeature.lowLevelFeatures`
- `SimilarityGroup.commonFeatures`
- `PossibleInterpretation`

生成规则：

1. 从 `InputFeature.lowLevelFeatures` 中统计出现频率最高的 feature key/value。
2. 优先选择有 evidence 的 feature。
3. 如存在 `SimilarityGroup.commonFeatures`，优先把 group 共同特征写入 summary。
4. summary 只做整体概览，不替代底层特征、分组和证据展示。
5. summary 必须使用倾向性语言。

默认模板：

```text
这组输入整体呈现出【共同特征 1】、【共同特征 2】和【共同特征 3】的倾向。系统只把这些视为本次样本中的可观察结构，而不是人格诊断或长期画像。
```

样本或证据不足时：

```text
当前样本中的共同结构还不稳定。系统仅整理已观察到的底层特征，并等待更多输入或反馈来确认这些倾向是否成立。
```

禁止：

- 不使用“你就是”“你一定”“你的本质”等确定性表达。
- 不使用“高级审美”“灵魂”“命运”等玄学或价值判断表达。

### 7.2 PossibleInterpretation 生成规则

数量规则：

- 默认生成 `1-2` 条。
- evidence 不足时只生成 `1` 条或不生成。
- 不强制满足“至少 2 条解释候选”的旧 prompt 文档要求；V1-C 以 evidence 充足为优先。

输入来源：

- `SimilarityGroup`
- `InputFeature`

evidenceRefs 规则：

- 必须引用 input id。
- 优先使用 similarity group 的 `inputIds`。
- 如果没有 group，则使用具备最多 feature evidence 的 input ids。
- 每条 interpretation 至少 1 个 evidenceRef。

confidence 规则：

- 默认 `0.62-0.72`。
- 有 similarity group 且 commonFeatures 非空：可提升到 `0.72`。
- 没有 group 或样本少：不高于 `0.62`。
- evidenceRefs 少于 2 个：不高于 `0.6`。

uncertainty 规则：

- 必须说明样本数量限制。
- 必须说明解释是候选，不是事实。

默认 uncertainty：

```text
样本数量仍然较少，该解释只表示当前输入中的一种可能观察，不代表稳定偏好。
```

### 7.3 Insight 生成规则

数量规则：

- 默认生成 `1-3` 条。
- 本轮优先生成 `1` 条重点洞察，避免为了数量编造。
- 每条 insight 必须有 `evidenceRefs` 和 `uncertainty`。

字段规则：

- `title`：倾向性表达，不做人格判断。
- `observation`：只写观察到的结构。
- `interpretation`：写可能解释，必须使用“可能”“倾向于”“在这组样本中”。
- `confidence`：默认 `0.64-0.72`，证据弱则降低。

evidenceRefs 规则：

- 至少 1 个 input id。
- 优先引用 similarity group 中的 inputs。
- 如果没有 group，引用 feature evidence 最多的 inputs。

禁止：

- 不输出心理诊断。
- 不输出人格标签。
- 不输出玄学表达。
- 不把相似性分组说成绝对聚类。

### 7.4 Confidence 降低规则

降低 confidence 的情况：

- 样本少于 3 个。
- 没有 similarity group。
- `commonFeatures` 为 `weak_shared_structure`。
- evidenceRefs 少于 2 个。
- feature evidence 为空或弱。

confidence 上限：

```text
样本少于 3 个：<= 0.55
没有 similarity group：<= 0.62
只有 1 个 evidenceRef：<= 0.60
存在 group 且 commonFeatures 明确：<= 0.72
```

本轮不做：

- 不展示复杂置信度可视化。
- 不把 confidence 当成准确率。

### 7.5 Feedback Schema 设计

本轮沿用当前 schema：

```text
rating: not_me | unsure | somewhat_me | very_me
comment?: string
```

采用原因：

- 已满足 insight-level granular feedback。
- 可以支持 V2 画像更新。
- 不需要提前扩张为复杂评估体系。

反馈作用边界：

- V1-C 只保存反馈。
- 不更新长期画像。
- 不改变当前报告。
- 不触发重新生成。

### 7.6 前端 Evidence 展示边界

当前前端已有：

- `InsightCard` 展示 insight evidenceRefs 对应输入。
- `FeedbackPanel` 支持 insight-level rating。
- report page 展示 summary、features、groups、interpretations、insights、disclaimer。

本轮前端原则：

- 不新增复杂 evidence drill-down。
- 不新增历史反馈展示。
- 不新增报告重生成。
- 如后端 response shape 不变，前端不改。

如果需要小改：

- 只允许文案级别调整，例如把 `Mock Report` 改成更准确的阶段提示。
- 不改变 route 或 API。

### 7.7 最终实现顺序

1. 调整 `MockInterpretationGenerator`，让 possible interpretations 基于 features / groups 生成。
2. 调整 `insights` 生成逻辑，让 insight 绑定具体 evidenceRefs。
3. 调整 `generate_report` summary，使其基于 features / groups / interpretations。
4. 保持 `ReportResponse` schema 不变。
5. 保持 feedback schema 不变。
6. 补充单元测试：summary、interpretation、insight、confidence 降低、禁用表达。
7. 补充集成测试：report 包含 evidenceRefs、uncertainty、feedback flow。
8. 运行 `python -m pytest` 和 `npm run build`。

## 8. 实现范围

### 8.1 Interpretation 生成

需要让 `PossibleInterpretation` 从当前 features / groups 中生成。

最低要求：

- 至少绑定 1 个 evidenceRef。
- 必须有 uncertainty。
- confidence 不超过本轮规则上限。
- evidence 不足时减少解释数量，而不是编造。

### 8.2 Insight 生成

需要让 `Insight` 从当前 features / groups / interpretations 中生成。

最低要求：

- 至少绑定 1 个 evidenceRef。
- 必须有 observation、interpretation、uncertainty。
- 不输出人格诊断、心理评估或玄学表达。

### 8.3 Report Summary

需要让 summary 基于 features / groups / interpretations 动态生成。

最低要求：

- 包含可观察共同特征。
- 使用倾向性语言。
- 不写长期画像。

### 8.4 Feedback

本轮保持当前 API 和 schema。

最低要求：

- 用户可以提交反馈。
- 反馈可以保存。
- feedback 不更新长期画像。

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

自动验证记录：

```text
2026-06-16：
- 已完成代码实现：summary 动态生成、PossibleInterpretation evidenceRefs、Insight evidenceRefs、confidence 降低规则、非诊断 uncertainty 文案。
- 已保持 ReportResponse schema 不变。
- 已保持 feedback schema / API 不变。
- 已新增 V1-C 单元测试。
- 已扩展 workflow 集成测试。
- `python -m pytest`：13 passed，3 warnings。
- `npm run build`：通过。

说明：
3 条 Pydantic UnsupportedFieldAttributeWarning 为既有 alias warning，未在 V1-C 中新增。
```

待人工验收：

```text
浏览器路径：上传不少于 3 条文字输入 → 生成报告 → 检查 summary / possibleInterpretations / insights / evidenceRefs / uncertainty → 提交 insight feedback。
```

人工验收记录：

```text
2026-06-16：
手动路径：上传不少于 3 条文字输入 → 生成报告 → 检查 summary / possibleInterpretations / insights / evidenceRefs / uncertainty → 提交 insight feedback。
结果：通过。
范围：V1-C report summary、possibleInterpretations、insights、evidenceRefs、uncertainty、insight feedback 保存提示。
限制：当前仍是 mock workflow，不接真实 LLM runtime；feedback 只保存，不更新长期画像。
```

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
