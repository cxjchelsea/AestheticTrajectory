# V3-A：Personalized History Retrieval

当前状态：

```text
research_realigned / pending_manual_validation
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V2 Memory / User Model baseline 之上，引入最小 personalized history retrieval：

```text
用户完成分析
↓
workflow 检索同用户历史报告与反馈
↓
生成 historyContext 并写入 report_json
↓
报告详情页展示“历史参考”
↓
每条历史参考保留 source refs，且与当前输入 evidence 分离
```

## 2. 上游版本决策

引用 `docs/iterations/v3-0-personalized-retrieval-research.md` 中已确认的版本级决策：

- V3-A 先做 personalized history retrieval，不做完整外部知识库 RAG。
- 历史检索结果是 `history_context`，不是新的当前输入证据。
- 被用户否定的解释只能作为 negative context，不能作为正向偏好。
- 当前输入 evidence 优先于历史检索。
- V3-A 不接入 ChromaDB runtime、LangSmith、OpenTelemetry、Agent / MCP。

## 3. 本轮解决什么问题

本轮解决：

```text
报告生成时能否参考用户历史报告和反馈，并在报告详情中可追溯展示？
```

本轮不解决：

- 外部审美知识库 RAG（V3-B）。
- 系统化 evaluation metrics（V3-C）。
- retrieval / RAG observability dashboard（V3-D）。
- V3-E 全量治理验收。
- ChromaDB / 真实 LLM / embedding runtime。

## 4. 外部调研与方案选择

本节在实现 V3-A 前完成；2026-06-17 流程重跑后，调研结论已回写实现。

调研层级：

```text
版本级：引用 docs/iterations/v3-0-personalized-retrieval-research.md §6.1–6.4
能力级：personalized history retrieval、history vs input evidence 边界
实现级：repository 检索方式、相关性过滤、排序、workflow 挂载、前端分区展示
```

### 4.1 调研问题

- 在用户历史报告规模较小时，是否必须先接向量库，还是可先用结构化/heuristic retrieval 验证边界？
- 历史报告与历史 feedback 应归类为哪种 memory / evidence type，如何避免与当前输入 evidence 混用？
- profile evidence 是否应进入 V3-A history context，还是与 episodic history 分离？
- 历史 feedback 是否必须满足与当前输入的特征相关性，才能进入 history context？
- 多条历史报告候选时，应按 recency 还是 relevance 排序？
- history context 应如何挂载与持久化，才能支持 trace 且报告详情一次 fetch？

### 4.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：Episodic memory 与 user scope

来源名称：Mem0 — Memory Types

来源类型：框架文档 / Agent memory 设计

链接或出处：`https://docs.mem0.ai/core-concepts/memory-types`

调研问题：

- 用户历史报告属于 episodic memory 还是 semantic memory？
- 检索时是否必须先做 user scope 过滤？

核心做法：

- 长期 memory 分 conversation / session / user / org 层；user memory 跨 session 持久化。
- 检索 pipeline 应优先 ranking user memories，并严格按 user scope 过滤。
- episodic memory 记录“过去发生过什么”，semantic memory 记录稳定偏好/事实。

对 V3-A 的启发：

- 历史 reports + feedback 属于 episodic memory，不是当前输入 primary evidence。
- 检索范围必须限定同用户；不能把 profile 正向证据再包装成 history item 重复注入。
- V3-A 可先验证 episodic retrieval 边界，不必立刻上 vector memory runtime。

不能照搬：

- 不引入 Mem0 API / 外部 memory store。
- 不把 history context 直接塞进 LLM 全量 prompt。

采用结论：

```text
V3-A 只检索同用户历史 reports / feedback；profile evidence 不在本子阶段重复注入 history context。
```

#### 记录 2：Scope filter 与 relevance filter 先于 ranking

来源名称：From RAG to Memory Systems: Building Stateful AI Architecture

来源类型：工程架构 / memory system 设计

链接或出处：`https://blogs.oracle.com/developers/from-rag-to-memory-systems-building-stateful-ai-architecture`

调研问题：

- 历史 feedback 是否可以在无特征重叠时仍进入 context？
- scope 与 relevance 应发生在排序前还是排序后？

核心做法：

- scope filter（user / tenant / project）必须在 ranking 之前执行，不能先 rank 再 filter。
- semantic discovery 场景需要 top-k + score threshold；低相关结果应 abstain。
- episodic memory 与 policy/preference memory 应使用不同 schema 与 lifecycle。

对 V3-A 的启发：

- 初版实现允许“无特征重叠的历史 feedback 仍进入 context”，存在 relevance 风险。
- feedback item 只能附着在有 feature overlap 的历史 report 上。
- 无 overlap 时应返回明确 message，而不是展示无关反馈。

不能照搬：

- 不做 multi-tenant hybrid retrieval pipeline。
- 不引入 vector + lexical fusion。

采用结论：

```text
V3-A 增加 relevance gate：仅当历史 report 与当前输入存在 feature overlap 时，才允许 report item 与 feedback item 进入 history context。
```

#### 记录 3：Overlap ranking 与 recency tie-break

来源名称：Agent Memory Systems: Building Long-Term Context for AI

来源类型：工程实践 / memory retrieval

链接或出处：`https://www.improving.com/thoughts/building-agent-memory-systems/`

调研问题：

- 没有 embedding runtime 时，如何做 deterministic retrieval？
- 多条历史候选时如何 rerank？

核心做法：

- top-k retrieval 常配合 reranking、recency bias、scope filtering。
- 小规模 personal corpus 可用规则/lexical overlap 先做 MVP，再演进到 semantic retrieval。
- 应优先注入高相关 memories，而不是简单截取最近 N 条。

对 V3-A 的启发：

- feature key overlap 可作为 V3-A 的 relevance score。
- 初版 `prior_reports[:5]` 按 recency 截断，可能漏掉 overlap 更高但较旧的历史报告。
- recency 只应作为 overlap 相同时的 tie-breaker。

不能照搬：

- 不引入 cross-encoder reranker 或 embedding rerank。
- 不做 access-frequency / importance scoring。

采用结论：

```text
V3-A 采用 overlap-count 降序 ranking；overlap 相同再按 repository recency；report items 取 top 5。
```

#### 记录 4：Evidence 类型分离与 citation

来源名称：Retrieval-Augmented Generation for Natural Language Processing: A Survey

来源类型：论文 / RAG survey

链接或出处：`https://arxiv.org/pdf/2407.13193`

调研问题：

- history context 与 insight evidenceRefs 应如何永久分离？
- feedback item 是否也需要 matchedFeatures / sourceRefs？

核心做法：

- 可控 RAG 需要 citation、abstention、answer-only-from-information。
- 不同 evidence source 必须可追踪，否则 retrieval 只会增加 hallucination 风险。

对 V3-A 的启发：

- `insight.evidenceRefs` 仍只指向当前输入。
- report / feedback items 都必须带 `sourceRefs`；feedback items 也应记录 `matchedFeatures`。
- disclaimer 必须说明历史参考不是人格/心理判断。

不能照搬：

- 不做 LLM grounding judge。
- 不把 history context 写入 profile positive evidence。

采用结论：

```text
V3-A 维持 historyContext 独立 schema；feedback items 补齐 matchedFeatures 与 sourceRefs。
```

### 4.3 方案对比

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | PostgreSQL + feature overlap + relevance gate | 可解释、可单测、与 V2 repository 一致 | 无语义相似度 | **采用** |
| B | ChromaDB / embedding semantic retrieval | 可找语义相近历史 | 超 V3-A 边界，依赖 mock embedding runtime | 拒绝 |
| C | 仅 recency 截取最近 N 条报告 | 实现最简单 | 可能注入低相关 feedback / 漏掉高 overlap 旧报告 | 拒绝 |

profile evidence 处理：

| 选项 | 结论 |
| --- | --- |
| 把 profile evidence 再包装成 history item | 拒绝；会与 V2 profile 通路重复，混淆 episodic / semantic memory |
| 仅使用 reports + feedback 构建 episodic history context | **采用** |

### 4.4 最终方案选择

#### 4.4.1 检索实现

采用：

```text
PostgreSQL / memory repository + feature overlap heuristic + relevance gate + overlap ranking
```

规则：

- 排除当前 report。
- 仅保留与当前输入存在 feature overlap 的历史 report。
- report items 按 overlap-count 降序，overlap 相同按 recency tie-break；最多 5 条。
- feedback items 只来自已有 overlap 的历史 report；补齐 matchedFeatures。
- 全部 items 截断至 8 条。

#### 4.4.2 历史上下文挂载方式

采用：

```text
workflow step 生成 PersonalHistoryContext，并作为 ReportResponse.historyContext 持久化
```

#### 4.4.3 前端展示

采用：

```text
ReportDetailPage 新增“历史参考”区块
```

规则：

- 明确区分“历史参考”和“当前输入证据”。
- 展示 summary、items、source refs、direction、matchedFeatures、disclaimer。
- 无历史或无相关 overlap 时显示 message，不伪装成真实偏好结论。

### 4.5 调研对实现的影响

相对初版实现，调研后调整：

| 项 | 初版 | 调研后 |
| --- | --- | --- |
| feedback 进入条件 | 任意历史 report 上的 feedback 都可能进入 | 仅当 parent report 与当前输入 feature overlap > 0 |
| report 候选排序 | `prior_reports[:5]` 按 recency 截取 | 按 overlap-count 降序，recency 作 tie-break |
| feedback item 字段 | 无 `matchedFeatures` | 补齐 `matchedFeatures` |
| profile evidence | 未纳入（与 V3-0 字面表述有差异） | 明确不纳入，避免 episodic / semantic 重复 |

代码影响：

- `backend/app/services/personal_history_retrieval.py`
- `backend/app/tests/unit/test_personal_history_retrieval.py`

## 5. 数据与 API 影响

新增 schema：

- `PersonalHistoryContext`
- `HistoryContextItem`

扩展 schema：

- `ReportResponse.historyContext`

新增 workflow step：

- `retrieve_personal_history`

不新增数据库表；history context 写入现有 `aesthetic_reports.report_json`。

## 6. 模块契约

### 6.1 `personal_history_retrieval` service

输入：

- 当前 report id
- 当前 features
- 用户历史 reports
- 用户 feedback

输出：

- `PersonalHistoryContext`

规则：

- 排除当前 report。
- 仅保留与当前输入存在 feature overlap 的历史 report。
- report items 按 overlap-count 降序，overlap 相同按 recency tie-break；最多 5 条。
- feedback items 只来自已有 overlap 的历史 report，并补齐 `matchedFeatures`。
- `very_me` / `somewhat_me` → positive context。
- `not_me` → negative context。
- `unsure` → neutral context。
- 所有 item 必须有 `sourceRefs`；全部 items 截断至 8 条。

### 6.2 workflow

顺序：

```text
extract_features
→ generate_embeddings
→ write_vectors
→ cluster_inputs
→ retrieve_personal_history
→ generate_report
→ save_report
```

## 7. 验收标准

功能：

- 第一份报告：`historyContext.message = 暂无可参考的历史报告。`
- 第二份及以后：若特征重叠，返回 report context items。
- 无特征重叠时：即使有历史 feedback，也不返回 feedback items；message 为“暂未找到与当前输入足够相关的历史参考。”
- 若存在与当前输入相关的历史 feedback，返回 positive / negative / neutral context items。
- overlap 更高的历史 report 排在更前。
- 报告详情页展示历史参考区块。

治理：

- insight.evidenceRefs 仍只指向当前输入。
- history context 不写入 profile positive evidence。
- summary / note 不输出人格、心理、能力诊断式表达。

测试：

- 单元测试：`test_personal_history_retrieval.py`
- 集成测试：`test_api_flow.py` 覆盖 workflow step 与第二份 report historyContext

## 8. 权威设计文档更新

本轮已上升：

- `docs/07-数据结构与系统架构文档.md`：补充 V3-A history context 边界。
- `docs/11-模块拆分与接口测试文档.md`：补充 V3-A personalized retrieval 实现契约。
- `docs/13-验证与评估文档.md`：补充 V3-A history context 治理检查。

## 9. 测试记录

```text
2026-06-17（初版）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，33 passed, 3 warnings。
- 前端：npm run build，通过。

2026-06-17（调研重对齐后）：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，41 passed, 3 warnings。
- 新增 relevance gate / overlap ranking 单测。
```

## 10. 人工验收

```text
待用户重新验收（调研重对齐后）：
- 完成两次特征重叠的分析后，第二份报告详情页出现“历史参考”。
- 历史 feedback 不会在无特征重叠时出现。
- overlap 更高的历史 report 优先展示。
- 历史参考带来源 refs / matchedFeatures，且与当前输入 evidence 分区展示。
- 第一份报告显示“暂无可参考的历史报告。”
- Developer Debug 中出现 retrieve_personal_history step。
```

## 11. 下一步

```text
用户完成 V3-A 重验收后，按同样流程重跑 V3-B（先调研、再方案、再实现）。
```
