# V1-B：Embedding 与相似性分组

当前状态：

```text
planned / research_required
```

创建日期：

```text
2026-06-16
```

## 1. 本轮目标

在 V1-A 已完成 `FeatureExtractor` 抽象和 `InputFeature` 校验的基础上，让系统能把多个审美输入组织成可解释的相似性结构。

本轮目标链路：

```text
InputFeature / 输入文本
↓
EmbeddingClient 抽象
↓
mock / real embedding 可切换
↓
embedding metadata 保存
↓
输入之间相似度计算
↓
小样本相似性分组
↓
SimilarityGroup 输出 commonFeatures / uncertainty
↓
继续复用现有报告生成和 API 行为
```

## 2. 当前基线

当前已归档状态：

```text
V1-A accepted / archived
```

已确认：

- `FeatureExtractor` 抽象已建立。
- `InputFeature` 已包含 `promptVersion` 和 `modelName`。
- `validate_input_feature` 已能拦截缺少 evidence 的 feature 输出。
- `MockEmbeddingClient` 已存在，可生成稳定 mock embedding。
- `EmbeddingRecord` schema 已存在，可记录 modelName、vectorDimension 和 chroma metadata。
- 当前 workflow 已有 `generate_embeddings`、`write_vectors`、`cluster_inputs` steps。
- 当前 `cluster_inputs` 仍是 mock：按 input ids 生成固定分组，不使用 embedding 距离。

当前限制：

- 未定义 `EmbeddingClient` 抽象。
- 未接入真实 embedding API。
- 未计算输入之间的相似度。
- 未基于 embedding 或 feature overlap 做真实分组。
- ChromaDB 仍是 mock metadata / 抽象替代，不做 runtime 写入验收。

## 3. 本轮解决什么问题

本轮解决：

```text
系统能否把多个审美输入组织成可解释、非绝对化的小样本相似性结构？
```

本轮不解决：

- 真实 PostgreSQL 持久化。
- 真实 ChromaDB runtime 写入。
- 历史报告。
- 长期用户画像。
- RAG。
- Agent。
- MCP。
- 报告页面大改。

## 4. 必须阅读的文档

只需要阅读以下文档：

1. `docs/04-审美表征体系文档.md`
2. `docs/05-AI分析逻辑文档.md`
3. `docs/09-AI Workflow 编排与任务执行文档.md`
4. `docs/10-Prompt Contract 与结构化输出规范.md`
5. `docs/13-验证与评估文档.md`
6. `docs/12-开发任务拆分与里程碑计划.md`
7. `docs/iterations/v1-a-real-feature-extraction.md`

不要一次性读取 `03-16` 全量文档。

## 5. 调研与方案选择

本节必须在实现 V1-B 代码前完成。

调研要求：

```text
本轮必须进行外部调研，并在本文档中记录。

不能只基于当前代码和通用工程经验直接设计。
不能只写“通用做法”，必须记录具体来源、可借鉴点、不能照搬点、最终采用 / 不采用理由。
```

### 5.1 调研问题

本轮调研只围绕 embedding 与小样本相似性分组：

- embedding 输入文本应该来自原始输入、`InputFeature` summary，还是二者组合？
- 图片真实分析尚未接入时，图片 input 应如何构造 embedding text？
- mock embedding 和未来真实 embedding 是否应共用同一个 `EmbeddingClient` 抽象？
- 小样本分组应该基于 cosine threshold、top-k、图连通分量，还是 feature overlap？
- `commonFeatures` 应该来自 feature key/value overlap，还是由 embedding 相似度反推？
- 样本少于 3 个时应该跳过分组，还是输出带强 uncertainty 的单组？
- 不接 ChromaDB runtime 时，如何明确“只是本地相似度计算”，避免误认为已经有真实向量检索？

### 5.2 已有实现调研

当前项目中已有：

- `MockEmbeddingClient`：可以把文本稳定映射为 8 维 mock vector。
- `EmbeddingRecord`：可记录 `ownerType`、`ownerId`、`collectionName`、`chromaId`、`modelName`、`vectorDimension`。
- `generate_embeddings`：当前直接实例化 `MockEmbeddingClient`。
- `write_vectors`：当前只写 embedding metadata，不写真实 ChromaDB runtime。
- `cluster_inputs`：当前通过 `MockInterpretationGenerator` 生成固定 mock group，不读取 embedding。
- `SimilarityGroup`：已有 `inputIds`、`commonFeatures`、`uncertainty`。

当前实现的主要问题：

- workflow 直接依赖 `MockEmbeddingClient`，没有 `EmbeddingClient` 抽象。
- embedding text 构造规则没有单独定义。
- 向量相似度没有计算。
- 分组结果与 embedding 无关。
- `commonFeatures` 当前不是从 feature overlap 计算出来的。

### 5.3 外部调研记录

当前状态：

```text
待调研
```

必须至少覆盖：

- embedding 输入构造：文本、结构化 feature summary、多模态输入如何转成 embedding text。
- embedding client 抽象：不同模型 / provider 的封装方式。
- 向量相似度：cosine similarity、dot product、归一化策略。
- 小样本分组：threshold grouping、top-k、图连通分量、feature overlap。
- 分组解释：如何生成 `commonFeatures` 和 uncertainty。
- 向量库边界：本轮不接 ChromaDB runtime 时，metadata 与真实检索能力如何区分。

调研记录格式：

```text
来源名称：
来源类型：文档 / 论文 / 产品 / 框架 / 博客 / API 文档
链接或出处：
调研问题：
核心做法：
可借鉴点：
不能照搬点：
对 V1-B 的影响：
采用 / 不采用结论：
```

外部调研完成后，需要把本节从 `待调研` 更新为具体记录。

### 5.4 可借鉴模式初稿

以下只是待验证的初稿，不能作为最终设计依据：

- embedding client 抽象：隔离 mock、真实 embedding API 和未来本地模型。
- cosine similarity：可能作为最小可解释相似度计算。
- threshold grouping：可能用于组织小样本。
- feature overlap：可能用于解释 commonFeatures，避免只凭向量黑盒生成结论。
- uncertainty 文案：需要明确样本少、阈值粗糙、mock embedding 的限制。

待调研确认后，才能决定是否采用。

### 5.5 可选方案

方案 A：只保留当前 mock group，不使用 embedding。

- 优点：改动最小。
- 问题：不能验证 V1-B 的核心问题。
- 结论：不采用。

方案 B：基于 mock embedding 做 cosine similarity，再用阈值形成小样本分组。

- 优点：能验证相似度计算和分组 workflow。
- 问题：mock embedding 不代表真实语义效果。
- 结论：待外部调研确认，当前只是候选。

方案 C：基于 `InputFeature` 的 feature overlap 分组，不使用 embedding。

- 优点：解释性更强。
- 问题：不能验证 embedding 链路。
- 结论：待外部调研确认，可能作为 `commonFeatures` 来源。

方案 D：直接接入真实 embedding API 和 ChromaDB runtime。

- 优点：更接近真实 V1。
- 问题：会扩大到模型配置、成本、runtime 依赖和向量库联调，不适合本轮。
- 结论：本轮不采用。

### 5.6 本轮待确认方案

当前暂定方案，外部调研完成前不能进入实现：

```text
EmbeddingClient 抽象
MockEmbeddingClient 默认保留
embedding text builder 明确规则
cosine similarity 计算
mock embedding + feature overlap 共同生成小样本分组
SimilarityGroup 输出 commonFeatures 和 uncertainty
ChromaDB 继续只记录 metadata 边界
```

正式实现前需要确认：

- embedding text builder 的字段优先级。
- 相似度阈值的初始值。
- 样本不足时的输出策略。
- `commonFeatures` 的生成规则。
- 外部调研记录已补齐。

## 6. 系统边界

本轮包含的能力：

- `EmbeddingClient` 抽象。
- embedding 输入文本构造。
- mock embedding 继续可用。
- cosine similarity 或等价稳定算法。
- 小样本 similarity group。
- group uncertainty。

本轮暂缓的能力：

- 真实 embedding API。
- ChromaDB runtime 写入和检索。
- 大规模聚类。
- 历史输入检索。

本轮明确不做：

- PostgreSQL runtime 持久化。
- 历史报告。
- 长期用户画像。
- RAG。
- Agent。
- MCP。
- 推荐系统。

边界原因：

```text
V1-B 只验证“当前一批输入能否形成可解释的相似性结构”。
真实向量库和历史检索属于后续持久化 / V3 检索增强范围。
```

## 7. 架构设计

本轮涉及的前端：

- 原则上不涉及。
- 只有在 `SimilarityGroup` schema 改动时才同步 TypeScript type。

本轮涉及的后端：

- `EmbeddingClient` 抽象。
- `generate_embeddings` step。
- `write_vectors` metadata step。
- `cluster_inputs` step。
- 相似度计算 helper。

本轮涉及的数据库：

- 不涉及真实数据库表。
- 继续使用当前 in-memory store 和 embedding metadata。

本轮涉及的 Agent Runtime：

- 不涉及。

本轮涉及的工具层：

- 不涉及外部工具。
- 不接真实 ChromaDB runtime。

本轮涉及的记忆层：

- 不涉及长期记忆。
- 只处理当前 analysis job 的一批输入。

本轮调用关系待设计：

```text
run_mock_aesthetic_analysis
↓
generate_embeddings(inputs, embedding_client)
↓
write_vectors(job, inputs, embeddings)
↓
cluster_inputs(input_ids, features, embeddings)
↓
SimilarityGroup / PossibleInterpretation / Insight
```

## 8. 模块契约

### 8.1 EmbeddingClient

模块职责：

- 接收文本，返回 vector。
- 暴露 `model_name` 和 `vector_dimension`。

上游模块：

- `generate_embeddings`。

下游模块：

- `write_vectors`。
- similarity calculation。

输入：

- 非空文本。

输出：

- `list[float]`。

异常情况：

- 输入为空。
- 输出向量为空。
- 输出维度不符合 client 声明。

权限边界：

- 只处理用户已提交输入派生出的文本。
- 不访问额外外部资源。

### 8.2 Similarity Calculator

模块职责：

- 计算两个 embedding vector 的相似度。

输入：

- 两个同维度非空向量。

输出：

- 0-1 或 -1-1 区间内的 similarity score，具体区间在实现前确认。

异常情况：

- 空向量。
- 维度不一致。

不涉及：

- 不访问 ChromaDB。
- 不保存业务数据。

### 8.3 Similarity Group Builder

模块职责：

- 根据当前 job 的输入、features 和 embeddings 生成小样本 `SimilarityGroup`。

输出：

- `SimilarityGroup[]`

必须包含：

- `inputIds`
- `commonFeatures`
- `uncertainty`

不涉及：

- 不做长期用户画像。
- 不做绝对聚类结论。
- 不修改 report API。

## 9. 实现范围

### 9.1 EmbeddingClient 抽象

需要定义统一抽象：

```text
EmbeddingClient
```

职责：

- 接收用于 embedding 的文本。
- 返回 `list[float]`。
- 暴露 `model_name` 和 `vector_dimension`。

要求：

- 保留当前 `MockEmbeddingClient`。
- 新增真实 embedding client 时不能破坏现有 mock workflow。
- workflow 不直接依赖具体 embedding 实现。

### 9.2 Embedding 输入文本构造

本轮需要明确 embedding 的输入来源。

最低要求：

- 文本输入优先使用 `contentText`。
- 图片输入在真实图片分析前，使用 `title`、`description` 或 feature summary 构造 embedding text。
- 不把空字符串送入 embedding client。
- 每个 input 都能生成 embedding 或被明确跳过并记录原因。

### 9.3 相似度计算

本轮需要新增基础相似度计算能力。

最低要求：

- 使用 cosine similarity 或等价稳定算法。
- 输入向量维度不一致时能识别错误。
- 空向量不能参与相似度计算。
- 相似度计算不依赖 ChromaDB runtime。

### 9.4 小样本相似性分组

本轮需要让 `cluster_inputs` 不再只按固定 mock 分组。

最低要求：

- 输入少于 3 个时可以跳过分组或输出明确 uncertainty。
- 相似输入可以进入同一组。
- 每组包含 `inputIds`、`commonFeatures`、`uncertainty`。
- 分组描述不能被写成绝对聚类结论。
- 分组可以先基于 mock embedding + feature overlap，不要求真实机器学习聚类。

### 9.5 Schema 与输出边界

本轮不新增复杂 schema，优先复用：

- `EmbeddingRecord`
- `SimilarityGroup`

如需补充字段，必须同步：

- 后端 Pydantic schema。
- 前端 TypeScript type。
- `docs/10-Prompt Contract 与结构化输出规范.md` 或对应设计文档。

## 10. 不允许 AI 自行决定的内容

本轮禁止自行扩大范围：

- 不新增历史报告。
- 不新增长期用户画像。
- 不新增 RAG。
- 不新增 Agent。
- 不新增 MCP。
- 不接入真实 PostgreSQL。
- 不接入真实 ChromaDB runtime。
- 不重构整个 workflow。
- 不改变现有 API 路径。
- 不删除 mock embedding client。
- 不把相似性分组描述为绝对聚类或人格判断。

## 11. 预期涉及文件

后端可能涉及：

```text
backend/app/ai/mock/mock_embedding.py
backend/app/schemas/embedding.py
backend/app/schemas/interpretation.py
backend/app/workflows/steps/generate_embeddings.py
backend/app/workflows/steps/write_vectors.py
backend/app/workflows/steps/cluster_inputs.py
backend/app/workflows/aesthetic_analysis_v1.py
backend/app/tests/unit/
backend/app/tests/integration/
```

如果新增真实 embedding client，建议放在：

```text
backend/app/ai/clients/
```

前端本轮原则上不改，除非 `SimilarityGroup` 或报告响应 schema 发生变化。

## 12. 验收标准

本轮完成需要满足：

- mock workflow 仍可运行。
- `python -m pytest` 通过。
- 前端 `npm run build` 仍通过。
- 每个有效 input 能生成 embedding。
- embedding metadata 能记录 `modelName` 和 `vectorDimension`。
- 相似度计算有单元测试覆盖。
- 相似输入能被分到同一组。
- 每个 similarity group 都有 `commonFeatures`。
- 每个 similarity group 都有 `uncertainty`。
- 样本不足时能跳过分组或给出明确 uncertainty。
- 报告仍然不包含人格诊断、玄学表达或绝对聚类结论。

## 13. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如有接口或 schema 变化，更新对应设计文档。

## 14. 下一轮入口

如果本轮通过，下一轮进入：

```text
V1-C：报告生成与反馈闭环
```

如果本轮未通过，继续收口：

```text
EmbeddingClient 抽象
相似度计算
小样本分组 uncertainty
```
