# V3-B：Aesthetic Knowledge RAG

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V3-A history context 之上，引入最小 aesthetic knowledge RAG：

```text
用户完成分析
↓
workflow 基于当前特征检索项目内置审美知识库
↓
生成 knowledgeContext 并写入 report_json
↓
报告详情页展示“知识参考”
↓
知识 reference 只用于解释风格概念，不进入 profile positive evidence
```

## 2. 上游版本决策

引用 `docs/iterations/v3-0-personalized-retrieval-research.md`：

- RAG 只做 explanation support，不做 preference evidence。
- 外部知识不得替代 input evidence。
- 不接入 ChromaDB runtime、LangSmith、OpenTelemetry。
- 不把知识库内容写入用户画像。

## 3. 外部调研与方案选择（补记）

本节为流程补记，原应在实现 V3-B 前完成；记录内容与已验收实现一致。

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.2、§6.3
能力级：aesthetic knowledge RAG、explanation support vs preference evidence
实现级：静态 knowledge chunks、feature tag 匹配、workflow 挂载、前端 citation 展示
```

### 3.1 调研问题

- V3-B 的最小知识库应做成向量 RAG，还是 curated static chunks + metadata/tag 匹配？
- 审美知识 reference 应如何与 insight evidence、history context 三分离？
- 无匹配知识时，系统应 abstain 还是让 LLM 自由发挥？
- knowledge context 是否允许进入 profile positive evidence？
- workflow 中 knowledge retrieval 与 history retrieval 的边界应如何在 debug 层显式标记？

### 3.2 外部调研记录

当前状态：

```text
completed（补记）
```

#### 记录 1：RAG 的正确定位是 explanation support

来源名称：Retrieval-Augmented Generation for Natural Language Processing: A Survey

来源类型：论文 / RAG survey

链接或出处：`https://arxiv.org/pdf/2407.13193`

调研问题：

- 外部知识库应提供什么类型的信息？
- 为什么 knowledge evidence 不能替代 user preference evidence？

核心做法：

- RAG 通过外部知识降低 parametric memory 依赖，但会引入 source control 与 grounding 问题。
- 对需要可控输出的应用，必须区分 primary evidence 与 supplementary knowledge。
- citation / source ref 是减少 hallucination 的基础机制。

对 V3-B 的启发：

- 审美知识库只解释风格概念，不代表“用户偏好事实”。
- `KnowledgeContextItem` 必须带 `sourceRefs`；不得写入 profile positive evidence。
- knowledge context 与 `insight.evidenceRefs`、history context 三者永久分区。

不能照搬：

- 不把外部知识 chunks 当作 user profile 更新来源。
- 不做开放式 web crawl 或大规模知识图谱。

采用结论：

```text
V3-B 定位为 explanation support RAG；knowledgeContext 独立 schema，带来源 citation，且不进入 profile positive evidence。
```

#### 记录 2：小型 curated knowledge base 的非向量 MVP

来源名称：KB-API — self-hosted markdown knowledge API with BM25

来源类型：开源实现 / 小型知识库检索实践

链接或出处：`https://github.com/teamerisingstars/KB-API`

调研问题：

- 在 chunk 数量很少时，是否值得先上 embedding + vector DB？
- 如何实现 honest “no answer” 路径？

核心做法：

- 小型 `.md` / curated corpus 可用 BM25、metadata filter 或 tag overlap 做 deterministic retrieval。
- 当 confidence 低于阈值时返回 `null`，不合成内容。
- answer 字段应是匹配段落本身，而不是 LLM 自由 paraphrase。

对 V3-B 的启发：

- V3-B 目标是验证 knowledge context 边界，不是搭建大规模 vector knowledge platform。
- 项目内置 `AestheticKnowledgeContext` + static chunks + feature tag overlap 足够支撑 MVP。
- 无匹配时必须返回明确 message，而不是伪造偏好或风格结论。

不能照搬：

- 不引入 BM25 / NLTK / 独立 KB-API 服务。
- 不做自然语言 question answering；只做 feature tag → knowledge chunk 匹配。

采用结论：

```text
V3-B 采用内置静态 knowledge chunks + feature tag 启发式匹配，top_k=3，score<=0 时不返回 item。
```

#### 记录 3：metadata / tag filtering 作为 embedding 前的可行路径

来源名称：LlamaIndex — Metadata Extraction and Filtering

来源类型：框架文档 / RAG indexing 实践

链接或出处：`https://docs.llamaindex.ai/en/stable/module_guides/indexing/metadata_extraction/`

调研问题：

- 在 embedding pipeline 未就绪时，如何用 metadata / tags 做 pre-filter？
- knowledge chunk 应携带哪些最小 metadata？

核心做法：

- chunk 可携带 tags、categories、section metadata，并在 retrieval 前先 filter。
- metadata filter 能显著降低 noise，且比 full vector search 更易测试。
- 对 domain-specific small KB，curated tags 往往比 generic embedding 更稳定。

对 V3-B 的启发：

- 每个 `KnowledgeChunk` 带 `feature_tags`、`title`、`snippet`、`sourceId`。
- 匹配逻辑基于 `feature key` 与 chunk tags 的 overlap score，结果 deterministic。
- 与 V3-A heuristic retrieval 保持同一 workflow step + pure function 模式。

不能照搬：

- 不引入 LlamaIndex runtime。
- 不做 LLM metadata extraction；tags 由项目维护者手工 curated。

采用结论：

```text
V3-B knowledge base 采用手工 curated feature_tags；service 层纯函数排序并截断 top_k。
```

#### 记录 4：前端 citation 与辅助区块展示

来源名称：RAGAS — Faithfulness metric concept

来源类型：评估框架文档 / grounding 概念

链接或出处：`https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/`

调研问题：

- 用户如何知道某段风格解释来自知识库，而不是模型臆测？
- Developer Debug 应如何区分 history retrieval 与 aesthetic knowledge RAG？

核心做法：

- faithfulness 要求 response claims 可被 retrieved context 支持。
- 在 UI 层，最轻量的 faithfulness 支撑是显式展示 retrieved snippet + source ref。
- retrieval / generation 组件应可分别 trace。

对 V3-B 的启发：

- 前端“知识参考”展示 title、snippet、source refs，与“历史参考”“重点洞察”分区。
- workflow 增加 `retrieve_aesthetic_knowledge` step；Developer Debug 对该 step 给出 boundary warning。
- disclaimer 明确“只用于解释风格概念，不代表用户偏好证据”。

不能照搬：

- V3-B 不接入 RAGAS runtime 或 LLM-as-judge。
- 不做 sentence-level claim extraction。

采用结论：

```text
V3-B 在前端与 debug trace 中显式展示 knowledge citation，并与 history retrieval 分 step、分区块。
```

### 3.3 最终方案选择

采用：

```text
内置静态 knowledge chunks + 特征标签启发式匹配
```

原因：

- 记录 1 明确 explanation support 边界；记录 2–3 支持 static curated KB + tag overlap MVP。
- V3-B 目标是验证 knowledge context 边界，不是搭建大规模向量知识库。
- 当前 mock feature extractor 输出稳定，可用 feature key 做 deterministic 匹配。
- 与 V3-A 的纯函数 + workflow step 模式一致。

## 4. 实现摘要

- 新增 `AestheticKnowledgeContext` / `KnowledgeContextItem` schema。
- 新增 `backend/app/ai/knowledge/aesthetic_knowledge_base.py` 静态知识条目。
- 新增 `aesthetic_knowledge_retrieval` service 与 `retrieve_aesthetic_knowledge` workflow step。
- `ReportResponse.knowledgeContext` 持久化到 `report_json`。
- 前端 `ReportDetailPage` 新增“知识参考”区块。
- Developer Debug 拆分 history retrieval 与 aesthetic knowledge RAG boundary warnings。

## 5. 验收标准

- 报告详情页展示知识参考，且带来源 refs。
- 知识 reference 与 insight evidenceRefs 分离。
- 知识 reference 不进入 profile positive evidence。
- 无匹配时返回明确 message，不伪造偏好结论。

## 6. 测试记录

```text
2026-06-17：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，36 passed, 3 warnings。
- 前端：npm run build，通过。
```

## 7. 人工验收

```text
2026-06-17：
- 用户已完成人工测试，V3-B 知识参考路径测试成功。
- 报告详情页出现“知识参考”区块。
- 每条知识参考包含 title、snippet、source refs。
- “知识参考”与“历史参考”“重点洞察”分区展示。
- Developer Debug 中出现 retrieve_aesthetic_knowledge step。
```

## 8. 下一步

```text
用户已完成 V3-B 人工验收；下一步进入 V3-C Evaluation Metrics Baseline。
```
