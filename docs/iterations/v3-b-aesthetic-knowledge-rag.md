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

引用 V3-A 已落地边界：

- retrieval 先做 relevance filter，再 ranking。
- supplementary context 与 insight evidenceRefs 永久分区。

## 3. 外部调研与方案选择

本节在实现 V3-B 前完成；2026-06-17 流程重跑后，调研结论已回写实现。

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.2、§6.3
能力级：aesthetic knowledge RAG、explanation support vs preference evidence
实现级：静态 knowledge chunks、feature tag 匹配、abstention、overlap ranking、workflow 挂载、前端 citation
```

### 3.1 调研问题

- 小型 curated corpus 是否应优先 metadata/tag 匹配，而不是 embedding + vector DB？
- 知识 reference 应如何与 insight evidence、history context 三分离？
- 小型知识库是否应更 aggressive 地 abstain，避免弱相关 chunk 被当作解释依据？
- 多条 chunk 候选时，应按什么规则 ranking？
- knowledge context 是否允许进入 profile positive evidence？
- workflow / debug 层应如何区分 history retrieval 与 aesthetic knowledge RAG？

### 3.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：RAG 的正确定位是 explanation support

来源名称：Retrieval-Augmented Generation for Natural Language Processing: A Survey

来源类型：论文 / RAG survey

链接或出处：`https://arxiv.org/pdf/2407.13193`

调研问题：

- 外部知识库应提供什么类型的信息？
- citation 是否是 V3-B 的必需项？

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

#### 记录 2：小型 corpus 应优先 abstention，而不是硬答

来源名称：How to Build RAG When Your Corpus Is Under 100 Documents

来源类型：工程实践 / small corpus RAG

链接或出处：`https://wiki.charleschen.ai/ai/processed/wiki/llm-core/rag/queries/getting-started/how-to-build-rag-for-a-small-corpus`

调研问题：

- chunk 很少时，是否仍应返回弱相关结果？
- 如何测试 abstention？

核心做法：

- 小型 corpus 覆盖率有限，应设置更 aggressive 的 retrieval threshold。
- 最佳匹配低于阈值时应明确 abstain，而不是用 tangentially relevant chunk 硬答。
- 必须单独测试 out-of-scope query 的 abstention。

对 V3-B 的启发：

- 初版实现只要 score > 0 就返回 item，对 out-of-scope feature 虽已 abstain，但缺少显式 threshold 常量与 out-of-scope 测试。
- 无 overlap 时必须返回明确 message，而不是伪造风格/偏好结论。
- 需要补 out-of-scope feature 的单测与 `MIN_FEATURE_OVERLAP` 常量。

不能照搬：

- 不引入 embedding similarity threshold 或 RAGAS runtime。
- 不做 100+ query golden set；只补关键 abstention / overlap 单测。

采用结论：

```text
V3-B 采用 MIN_FEATURE_OVERLAP=1 的 abstention gate；无匹配时返回“暂未找到与当前输入足够相关的审美知识参考。”
```

#### 记录 3：metadata / tag filtering 作为 embedding 前的可行路径

来源名称：Metadata-Based Filtering in RAG Systems

来源类型：课程文档 / RAG filtering 实践

链接或出处：`https://codesignal.com/learn/courses/scaling-up-rag-with-vector-databases/lessons/metadata-based-filtering-in-rag-systems`

调研问题：

- 在 embedding pipeline 未就绪时，如何用 metadata / tags 做 pre-filter？
- 多条 chunk 候选时如何减少 noise？

核心做法：

- 先用 metadata filter 缩小候选，再做 relevance ranking。
- 对 domain-specific small KB，curated tags 往往比 generic embedding 更稳定。

对 V3-B 的启发：

- 每个 `KnowledgeChunk` 带 `feature_tags`、`title`、`snippet`、`source`。
- 匹配逻辑基于 feature key overlap count，结果 deterministic。
- 与 V3-A heuristic retrieval 保持同一 workflow step + pure function 模式。

不能照搬：

- 不引入 ChromaDB / vector DB filter API。
- 不做 LLM metadata extraction；tags 由项目维护者手工 curated。

采用结论：

```text
V3-B 采用手工 curated feature_tags + overlap-count ranking；不引入 vector runtime。
```

#### 记录 4：overlap ranking 与稳定 tie-break

来源名称：RAG knowledge base: answers grounded in sources, never invented

来源类型：工程实践 / grounded RAG

链接或出处：`https://www.tmmagency.com/en/rag-knowledge-base-that-does-not-invent/`

调研问题：

- 多条 chunk 分数接近时，如何避免不稳定结果？
- UI 层如何支撑 grounding？

核心做法：

- 检索结果应可追溯到 source metadata；低于 grounding threshold 时不应输出。
- 每条 fragment 应携带 source metadata，作为 citation 基础。
- 对 small KB，确定性 ranking 比复杂 rerank 更适合 MVP。

对 V3-B 的启发：

- 初版按 score 排序但未定义 tie-break，测试结果可能不稳定。
- 应像 V3-A 一样采用 overlap-count 降序 + 稳定 secondary key（docId）。
- 前端“知识参考”展示 title、snippet、matchedFeatures、source refs。

不能照搬：

- 不做 LLM grounding judge 或 delivery-time faithfulness check。
- 不引入权限 metadata filter。

采用结论：

```text
V3-B 采用 overlap-count 降序 ranking，tie-break 使用 docId；前端与 debug trace 分 step、分区块展示 citation。
```

### 3.3 方案对比

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 静态 curated chunks + feature tag overlap + abstention gate | 可解释、可单测、零 vector 依赖 | 无语义相似度 | **采用** |
| B | ChromaDB / embedding semantic retrieval | 可找语义相近概念 | 超 V3-B 边界，依赖 mock embedding runtime | 拒绝 |
| C | 任意 score>0 的 chunk 直接返回 | 实现最简单 | 弱相关 chunk 可能污染解释 | 拒绝 |

knowledge vs profile 处理：

| 选项 | 结论 |
| --- | --- |
| 把 knowledge context 写入 profile positive evidence | 拒绝；知识是 explanation support，不是 preference evidence |
| 仅挂载到 `ReportResponse.knowledgeContext` | **采用** |

### 3.4 最终方案选择

采用：

```text
内置静态 knowledge chunks + feature tag overlap + MIN_FEATURE_OVERLAP gate + overlap ranking
```

规则：

- 从当前输入提取 feature key（仅含 evidence 的信号）。
- 仅保留 overlap >= 1 的 chunk。
- 按 overlap-count 降序，tie-break 使用 docId；最多 top 3。
- 无匹配时返回明确 message，不伪造偏好或风格结论。
- 每条 item 带 matchedFeatures、sourceRefs、note、disclaimer。

### 3.5 调研对实现的影响

相对初版实现，调研后调整：

| 项 | 初版 | 调研后 |
| --- | --- | --- |
| overlap threshold | `score <= 0` 隐式判断 | 显式 `MIN_FEATURE_OVERLAP = 1` |
| chunk 排序 | 仅按 score 降序 | overlap-count 降序 + docId tie-break |
| out-of-scope abstention | 行为已有，缺测试 | 补 out-of-scope feature 单测 |
| overlap 优先级 | 缺断言 | 补高 overlap chunk 优先单测 |

代码影响：

- `backend/app/services/aesthetic_knowledge_retrieval.py`
- `backend/app/tests/unit/test_aesthetic_knowledge_retrieval.py`

## 4. 实现摘要

- 新增 `AestheticKnowledgeContext` / `KnowledgeContextItem` schema。
- 新增 `backend/app/ai/knowledge/aesthetic_knowledge_base.py` 静态知识条目。
- 新增 `aesthetic_knowledge_retrieval` service 与 `retrieve_aesthetic_knowledge` workflow step。
- `ReportResponse.knowledgeContext` 持久化到 `report_json`。
- 前端 `ReportDetailPage` 新增“知识参考”区块。
- Developer Debug 拆分 history retrieval 与 aesthetic knowledge RAG boundary warnings。

## 5. 模块契约

### 5.1 `aesthetic_knowledge_retrieval` service

输入：

- 当前 features
- top_k（默认 3）

输出：

- `AestheticKnowledgeContext`

规则：

- 仅匹配与当前输入 feature key 有 overlap 的 chunk。
- overlap-count 降序，docId tie-break。
- 所有 item 必须有 `sourceRefs` 与 `matchedFeatures`。
- 不写入 profile positive evidence。

### 5.2 workflow

顺序片段：

```text
retrieve_personal_history
→ retrieve_aesthetic_knowledge
→ generate_report
→ compute_report_evaluation
→ save_report
```

## 6. 验收标准

功能：

- 报告详情页展示“知识参考”，且带来源 refs / matchedFeatures。
- mock 特征（低饱和、低密度、非人物中心）应匹配对应知识条目。
- out-of-scope feature 时返回明确 abstention message。
- overlap 更高的 chunk 排在更前。

治理：

- 知识 reference 与 insight evidenceRefs 分离。
- 知识 reference 不进入 profile positive evidence。
- summary / note 不输出人格、心理、能力诊断式表达。

测试：

- 单元测试：`test_aesthetic_knowledge_retrieval.py`
- 集成测试：`test_api_flow.py` 覆盖 workflow step 与 knowledgeContext

## 7. 权威设计文档更新

本轮已上升：

- `docs/11-模块拆分与接口测试文档.md`：补充 V3-B overlap ranking / abstention 测试说明。
- `docs/13-验证与评估文档.md`：补充 V3-B out-of-scope abstention 治理检查。

## 8. 测试记录

```text
2026-06-17（初版）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，36 passed, 3 warnings。

2026-06-17（调研重对齐后）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，43 passed, 3 warnings。
- 新增 MIN_FEATURE_OVERLAP gate、overlap ranking tie-break、out-of-scope abstention 单测。
```

## 9. 人工验收

```text
2026-06-17（调研重对齐后，用户人工验收通过）：
- 报告详情页出现“知识参考”区块。
- 每条知识参考包含 title、snippet、matchedFeatures、source refs。
- “知识参考”与“历史参考”“重点洞察”“质量评估”分区展示。
- Developer Debug 中出现 retrieve_aesthetic_knowledge step。
```

## 10. 下一步

```text
V3-B 重验收已通过；V3-C 按同样流程重跑中。
```
