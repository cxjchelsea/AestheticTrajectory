# V4-C：Knowledge Graph & External RAG Runtime

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-18
```

## 1. 本轮目标

在 V3-B 静态审美知识库与 V4-A Chroma runtime 地基之上，建立 **可追溯概念图谱 + 可更新知识检索**：

```text
curated 审美概念 + 关系边（带 sourceEvidence）
↓
知识 chunk 可 seed / 扩展，可选向量入库 Chroma
↓
retrieve_aesthetic_knowledge 升级为 tag 匹配 + 图谱邻接 + 可选 vector rerank
↓
knowledgeContext 增强（相关概念、关系说明、sourceRefs）
↓
只读图谱查询 API + 报告页 / debug 可观测
```

本轮完成后，用户应能：

- 在报告详情看到比 V3-B 更丰富的「知识参考」（含相关概念与关系说明）。
- 通过 API 只读浏览概念节点与关系边，且每条边可展开 `sourceEvidence`。
- 在 debug 面板看到 knowledge/graph retrieval trace（检索路径、abstention 原因）。
- 确认知识/图谱 **不进入** profile positive evidence（V3 治理仍成立）。

## 2. 上游版本决策

引用 `docs/iterations/v4-0-long-term-personalized-agent-research.md` §7.4、§V4-C：

- V4-C 在 V4-B 之后、V4-D 之前；**不**依赖 Agent、MCP 生产接入。
- 图谱边必须有 `sourceEvidence`；无证据不建边。
- 图谱与外部 RAG **不写入** profile positive evidence。
- 与 V3 `knowledgeContext` 兼容：可 enrich items，**不破坏** abstention 语义。

引用 `docs/19-记忆与用户模型设计文档.md` §10.2：

- 概念关系边必须有 sourceEvidence。
- 知识检索结果仍为 supplementary context。

引用 V3-B 已落地边界（`docs/iterations/v3-b-aesthetic-knowledge-rag.md`）：

- 小型 curated corpus 优先 tag/metadata 匹配；abstention 优先于弱相关引用。
- `historyContext` / `knowledgeContext` / insight `evidenceRefs` 三分离。

引用 V4-A：

- 可选 Chroma collection：`knowledge_{runtime}_{dimension}`（与 `inputs_*` 分 collection）。
- `CHROMA_ENABLED=false` 时仍可用 tag + graph 检索，向量路径 skipped。

## 3. 本轮解决什么问题

本轮解决：

```text
如何在不大改 V3-B 解释边界的前提下，引入可追溯的审美概念关系，并可选接入向量检索以增强 chunk 召回？
```

本轮不解决：

- MCP 外部收藏/笔记导入（V4-D）。
- 全自动知识 crawl、LLM 自动建边。
- Neo4j / 重型图数据库。
- Agent 工具编排（V4-D）。
- 把图谱关系或 RAG 结果写入 profile / timeline 正向证据。
- 生产级外部 API 知识源同步。

## 4. 当前实现快照（V4-C 起点）

| 能力 | 当前状态 |
| --- | --- |
| 知识 chunk | `AESTHETIC_KNOWLEDGE_CHUNKS` 静态 tuple（4 条） |
| 检索 | `build_aesthetic_knowledge_context`：feature tag overlap，top_k=3 |
| 图谱 | **无** concept / relation 模型与 API |
| 向量检索 | V4-A 仅 `inputs_*` collection；知识 chunk **未**向量化 |
| 报告展示 | V3-B「知识参考」区块 |
| Debug | `retrieve_aesthetic_knowledge` step + boundary `dev_only` |

## 5. 外部调研与方案选择

调研层级：

```text
版本级：引用 v4-0 §7.4
能力级：轻量 KG vs 全量 RAG、explanation-only 边界
实现级：PostgreSQL 邻接表 vs 内存 seed、Chroma knowledge collection
```

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| 图谱存哪？ | **PostgreSQL 邻接表** + seed migration；测试用 memory repository |
| 图查询深度 | **1-hop** 邻接扩展（V4-C 范围）；不做多跳推理 |
| 向量检索 | **可选**：`CHROMA_ENABLED` 时对 knowledge chunks upsert + query；默认仍 tag-first |
| 与 V3-B 关系 | **增强** `retrieve_aesthetic_knowledge`；保留 tag overlap + abstention |
| 边如何创建 | **curated seed + 管理 API 只读**；V4-C 不做开放写 API |
| LLM 建边 | **拒绝**；边必须来自 curated sourceEvidence |

### 5.2 外部调研记录

#### 记录 1：RAG 用于 explanation support（非 preference）

来源名称：Retrieval-Augmented Generation for NLP: A Survey

来源类型：论文 / survey

链接或出处：`https://arxiv.org/pdf/2407.13193`

调研问题：

- RAG 在解释型系统中的边界是什么？

核心做法：

- 检索增强应明确区分「外部知识」与「用户事实」；引用需可追溯。

对 V4-C 的启发：

- `knowledgeContext` 继续 supplementary；graph 只扩展解释 vocabulary，不写入 profile。

采用结论：

```text
V4-C 保持 explanation-only；graph/RAG 输出只进入 knowledgeContext。
```

#### 记录 2：轻量知识图谱用于可解释推荐/解释

来源名称：工程实践 / v4-0 §7.4

来源类型：版本级决策

调研问题：

- MVP 是否需要 Neo4j？

核心做法：

- 概念 + 轻量谓词（related_to, contrasts_with, example_of）+ sourceEvidence 足够支撑可解释引用。

对 V4-C 的启发：

- 用 relational 表表达 concepts + relations；API 只读查询。

采用结论：

```text
PostgreSQL 轻量图谱，不做独立图数据库。
```

#### 记录 3：V3-B tag 匹配 baseline

来源名称：项目已实现 `aesthetic_knowledge_retrieval.py`

来源类型：项目代码 / V3-B

调研问题：

- V4-C 是否替换 V3-B 检索？

核心做法：

- feature tag overlap + MIN_FEATURE_OVERLAP + abstention message。

对 V4-C 的启发：

- V4-C **保留** tag 匹配为主路径；graph/vector 为 enrich 层，tag 无匹配时仍 abstain。

采用结论：

```text
tag-first → graph expand → optional vector rerank；无匹配则 abstain。
```

### 5.3 方案对比

#### 图谱存储

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 纯 JSON 文件 | 简单 | 难版本化、无查询 API | 拒绝 |
| B PostgreSQL concepts + relations | 可 migration seed、可测试 | 需 schema | **采用** |
| C Neo4j | 图查询强 | 超 V4-C 范围 | 拒绝 |

#### 向量检索

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 仅 tag/graph | 零外部依赖 | 召回有限 | 默认路径 |
| B tag/graph + Chroma knowledge collection | 复用 V4-A | 需 embedding 一致 | **可选采用** |
| C 替换为纯 vector RAG | 召回高 | 破坏 V3 abstention 语义 | 拒绝 |

## 6. 系统边界

### 6.1 必做

- [x] Schema + migration：`aesthetic_concepts`、`aesthetic_concept_relations`（含 source_evidence_json）。
- [x] Seed：从现有 `AESTHETIC_KNOWLEDGE_CHUNKS` + 少量概念关系迁移入库。
- [x] `KnowledgeGraphRepository`（memory + database）。
- [x] 升级 `build_aesthetic_knowledge_context`：tag 匹配 + 1-hop 相关概念/边。
- [x] 扩展 `KnowledgeContextItem`（如 `relatedConceptIds`、`relationNotes`，向后兼容）。
- [x] 只读 API：`GET /api/aesthetic-knowledge/concepts`、`GET /api/aesthetic-knowledge/graph`。
- [x] Debug trace：graph hit count、vector skipped/used、abstention reason。
- [x] 报告页展示相关概念（只读 citation）。
- [x] 单元/集成测试 + V3 governance 回归。
- [ ] 上升 `07` / `11` / `19` §10.2；`15` 记录。

### 6.2 可选（CHROMA_ENABLED 时）

- [x] `knowledge_vectors` upsert on seed/startup 或 lazy on first query。
- [x] vector rerank top chunks after tag filter。

### 6.3 不做

- [ ] MCP / 外部 crawl / 用户上传知识库。
- [ ] 图谱边 LLM 自动生成。
- [ ] 图谱写入 profile / timeline。
- [ ] Agent 工具调用壳（V4-D）。

## 7. 架构影响

### 7.1 数据模型（拟采用）

```text
aesthetic_concepts
  id, slug, label, description, feature_tags_json, source_refs_json, created_at

aesthetic_concept_relations
  id, from_concept_id, to_concept_id, predicate, source_evidence_json, created_at
```

`predicate` 枚举（首版）：`related_to` | `contrasts_with` | `example_of`

`source_evidence_json` 最低字段：

```json
{ "docIds": ["kb_low_saturation_space"], "note": "curated from project knowledge v1" }
```

Chroma（可选）：

```text
collection: knowledge_{runtime}_{dimension}
metadata: docId, conceptIds[], featureTags[]
```

### 7.2 API 设计（拟）

| 路径 | 方法 | 说明 |
| --- | --- | --- |
| `/api/aesthetic-knowledge/concepts` | GET | 列表；可选 `?featureTag=` 过滤 |
| `/api/aesthetic-knowledge/concepts/{id}` | GET | 单概念 + 出边/入边 |
| `/api/aesthetic-knowledge/graph` | GET | `?conceptId=` 返回 1-hop 子图 |
| `/api/aesthetic-knowledge/chunks` | GET | 只读 chunk 列表（兼容 V3 docId） |

workflow 仍通过 `retrieve_aesthetic_knowledge` step 写入 report；不新增用户触发分析 API。

### 7.3 模块与目录（拟）

```text
backend/app/schemas/knowledge_graph.py
backend/app/models/persistence.py          # ConceptModel, RelationModel
backend/app/repositories/knowledge_graph_repository.py
backend/app/services/knowledge_graph_query.py
backend/app/services/aesthetic_knowledge_retrieval.py  # 升级
backend/app/vector_store/knowledge_vector_store.py     # 可选
backend/app/api/routes/aesthetic_knowledge.py
frontend/src/pages/ReportDetailPage.tsx              # 知识参考增强
frontend/src/services/knowledgeApi.ts
```

### 7.4 检索流程（拟）

```text
extract_features
→ retrieve_aesthetic_knowledge
    1. feature tag overlap on chunks（V3-B）
    2. map matched chunks → concepts
    3. 1-hop graph expand（带 predicate + sourceEvidence）
    4. optional: vector query on knowledge collection
    5. assemble KnowledgeContextItem[] + abstention if empty
→ generate_report（knowledge 仍为 supplementary）
```

### 7.5 治理不变量

1. 无 sourceEvidence 的边不返回给 UI/API。
2. knowledge/graph 文本不得进入 profile positive evidence（沿用 V3-E 测试）。
3. abstention 消息保持诚实（「暂未找到足够相关…」）。
4. debug 必须区分 tag / graph / vector 路径。

## 8. 验收标准

### 8.1 自动测试

- memory backend pytest 全量通过。
- tag 无匹配 → abstention（V3-B 兼容）。
- 有匹配 → items 含 docId + sourceRefs；graph 扩展后含 relation 说明。
- governance：knowledge 不 feed profile positive evidence。
- API：concepts/graph 只读；非法 id 404。

### 8.2 人工验收清单

- [x] 分析后报告「知识参考」出现相关概念/关系说明。
- [x] 图谱 API 可浏览 seed 概念与边，边可展开 sourceEvidence。
- [x] `CHROMA_ENABLED=true` 时 debug 显示 knowledge vector 路径（可选）。
- [x] profile 页不因知识检索新增正向倾向。
- [x] V3-E governance 测试仍全部通过。

## 9. AI 生成代码顺序（确认后执行）

1. Schema + migration + seed + repository
2. `knowledge_graph_query` + unit tests
3. 升级 `aesthetic_knowledge_retrieval` + workflow 兼容
4. aesthetic-knowledge API routes
5.（可选）knowledge Chroma upsert/query
6. Frontend 报告页 + knowledgeApi
7. Debug trace 扩展 + governance tests
8. 上升 `07` / `11` / `19` + `15` 记录

## 10. 权威设计文档更新判断

实现开始前更新：

- `docs/07`：concepts / relations 表、Chroma knowledge collection
- `docs/11`：knowledge graph 模块契约
- `docs/19` §10.2：从占位改为实现映射

## 11. 用户确认（已接受）

- [x] 接受 **PostgreSQL 轻量图谱**（concepts + relations），不用 Neo4j。
- [x] 接受 **tag-first + 1-hop graph expand** 检索策略；向量检索为可选增强。
- [x] 接受首版 **只读** 图谱 API（curated seed，无开放写边）。
- [x] 接受 **不** 接入 MCP / 外部 crawl（留 V4-D）。
- [x] 接受 knowledge/graph **不进入** profile positive evidence（继承 V3 治理）。

## 12. 当前结论

```text
V4-C 已验收通过，状态 accepted / manual_validation_passed。
自动测试：79 passed（memory backend）；database + Chroma 人工验收通过。
下一步：启动 V4-D（Agent / MCP runtime）方案调研。
```
