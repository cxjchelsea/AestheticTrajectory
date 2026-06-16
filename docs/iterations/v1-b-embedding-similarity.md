# V1-B：Embedding 与相似性分组

当前状态：

```text
accepted / archived
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
completed
```

#### 记录 1：OpenAI Vector Embeddings

来源名称：OpenAI Vector embeddings

来源类型：API 文档

链接或出处：`https://developers.openai.com/api/docs/guides/embeddings`

调研问题：

- embeddings 能否用于 clustering、recommendations、search 等任务？
- 应该使用什么距离函数比较 embedding？

核心做法：

- 文本被转换为浮点向量。
- embeddings 可用于 search、clustering、recommendations、anomaly detection、classification。
- OpenAI 推荐 cosine similarity。
- OpenAI embeddings 归一化到长度 1，因此 cosine similarity、dot product 和 Euclidean ranking 在排序上可等价或接近。

可借鉴点：

- V1-B 可以用 cosine similarity 作为最小相似度计算。
- `EmbeddingClient` 需要记录 `modelName` 和 `vectorDimension`。
- embedding 可用于 grouping，但 grouping 结果需要解释层补充，不能只输出向量距离。

不能照搬点：

- 本轮不直接接 OpenAI embedding API。
- 本轮不做大规模向量检索或推荐系统。
- 不能把 mock embedding 相似性当成真实用户长期偏好。

对 V1-B 的影响：

- 采用 cosine similarity 作为默认相似度函数。
- 保留未来真实 embedding provider 替换空间。

采用 / 不采用结论：

- 采用 cosine similarity 思路。
- 暂不采用真实 OpenAI embedding runtime。

#### 记录 2：OpenAI Embeddings FAQ

来源名称：OpenAI Embeddings FAQ

来源类型：帮助文档

链接或出处：`https://help.openai.com/en/articles/6824809-embeddings-faq`

调研问题：

- 快速检索大量 embedding 是否需要向量数据库？
- distance function 是否必须复杂选择？

核心做法：

- 大量向量快速检索推荐使用 vector database。
- 距离函数通常不需要过度复杂化，推荐 cosine similarity。
- OpenAI embeddings 归一化后 dot product 可更快。

可借鉴点：

- 当前小样本阶段可以不接 ChromaDB runtime。
- 后续进入大量历史输入或 V3 检索增强时，再引入真实向量数据库。

不能照搬点：

- FAQ 面向真实 OpenAI embedding，不适用于当前 mock embedding 效果判断。
- 不能因为文档推荐 vector database 就提前接 ChromaDB runtime。

对 V1-B 的影响：

- V1-B 聚焦本地 pairwise similarity。
- ChromaDB 继续明确为 metadata / 后续 runtime 边界。

采用 / 不采用结论：

- 采用“小样本本地计算、大规模再接向量数据库”的边界。

#### 记录 3：Sentence Transformers Semantic Textual Similarity

来源名称：Sentence Transformers Semantic Textual Similarity

来源类型：开源库文档

链接或出处：`https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html`

调研问题：

- 句子 embedding 如何计算语义相似度？
- similarity matrix 是否适合当前一批输入之间的 pairwise comparison？

核心做法：

- 先为文本生成 embeddings，再计算相似度。
- `model.similarity(embeddings1, embeddings2)` 返回所有 pair 的 similarity matrix。
- 默认 similarity function 是 cosine。
- 如果 embedding 已归一化，dot product 可作为更快替代。

可借鉴点：

- V1-B 可生成当前 job 内所有输入的 pairwise similarity matrix。
- 对当前 3-10 个输入，小矩阵计算足够简单可解释。
- similarity matrix 可作为后续 group builder 的输入。

不能照搬点：

- 本轮不引入 Sentence Transformers 依赖。
- 不接本地模型下载、GPU、模型缓存等运行时复杂度。

对 V1-B 的影响：

- 设计 `similarity_matrix` 或 pairwise score helper。
- 当前实现优先纯 Python / mock vector，不新增 ML 依赖。

采用 / 不采用结论：

- 采用 pairwise similarity matrix 思路。
- 不采用 Sentence Transformers runtime。

#### 记录 4：scikit-learn cosine_similarity

来源名称：scikit-learn `cosine_similarity`

来源类型：开源库 API 文档

链接或出处：`https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html`

调研问题：

- cosine similarity 的定义和输入输出约束是什么？
- 空向量、维度不一致时应该如何处理？

核心做法：

- cosine similarity 是归一化 dot product：`K(X, Y) = <X, Y> / (||X|| * ||Y||)`。
- `Y=None` 时，返回 `X` 内所有样本之间的 pairwise similarities。
- 对 L2-normalized 数据，cosine similarity 等价于 linear kernel。

可借鉴点：

- V1-B 实现可按该公式写轻量 helper。
- 需要显式校验空向量和维度不一致。
- similarity matrix 应该和输入顺序保持一致。

不能照搬点：

- 本轮不必新增 scikit-learn 依赖。
- 不需要支持 sparse matrix 或大型数据优化。

对 V1-B 的影响：

- 新增 `cosine_similarity` helper。
- 单元测试覆盖相同向量、正交向量、空向量、维度不一致。

采用 / 不采用结论：

- 采用公式和校验思路。
- 不采用 scikit-learn runtime 依赖。

#### 记录 5：scikit-learn Clustering / Agglomerative / DBSCAN

来源名称：scikit-learn clustering documentation

来源类型：开源库文档

链接或出处：`https://sklearn.org/stable/modules/clustering.html`

调研问题：

- 小样本相似性分组可以参考哪些聚类策略？
- 什么时候不适合 K-Means？

核心做法：

- Agglomerative clustering 可以使用 cosine distance，适合层次合并。
- DBSCAN 使用密度概念，需要选择 `eps` 和 `min_samples`。
- K-Means 通常要求预设 cluster 数量，且默认更偏 Euclidean 空间。
- 预计算 similarity 用于 clustering 时，通常需要转换为 distance，例如 `1 - similarity`。

可借鉴点：

- V1-B 不适合一上来用 K-Means，因为用户输入只有 3-10 个样本，cluster 数量不稳定。
- 可以借鉴 threshold / graph connected components：相似度超过阈值就连边，再形成小组。
- 样本不足或没有强相似边时，应输出 uncertainty，而不是强行聚类。

不能照搬点：

- 本轮不引入完整聚类库。
- 不做 DBSCAN / Agglomerative runtime。
- 不输出“绝对聚类结论”。

对 V1-B 的影响：

- 初始采用阈值连边 + 连通分量方式，比 K-Means 更适合小样本。
- uncertainty 必须说明阈值和样本数量限制。

采用 / 不采用结论：

- 采用 threshold graph 的小样本分组思想。
- 不采用 K-Means / DBSCAN / Agglomerative 依赖。

#### 记录 6：ChromaDB Collections / Query

来源名称：ChromaDB collection add / query documentation

来源类型：向量数据库文档

链接或出处：

- `https://docs.trychroma.com/docs/collections/add-data`
- `https://docs.trychroma.com/docs/querying-collections/query-and-get`

调研问题：

- ChromaDB 存储什么？
- metadata 与真实向量检索能力的边界是什么？

核心做法：

- collection 可保存 `ids`、`documents`、`embeddings`、`metadatas`。
- 如果已经计算 embedding，可以直接传入 embeddings。
- query 用于 nearest-neighbor similarity search。
- query embedding 维度必须匹配 collection embedding 维度。
- `where` 可过滤 metadata，`where_document` 可过滤文本内容。

可借鉴点：

- `EmbeddingRecord` 记录 `collectionName`、`chromaId`、`modelName`、`vectorDimension` 是合理的 metadata 边界。
- 真实 ChromaDB runtime 接入时，需要确保 embedding 维度一致。
- metadata 不能替代业务数据库，也不能表示已经做了真实向量检索。

不能照搬点：

- 本轮不调用 ChromaDB `.add()` 或 `.query()`。
- 不把 ChromaDB 当业务数据库。
- 不用 metadata 假装完成 runtime 写入。

对 V1-B 的影响：

- 本轮继续只保存 embedding metadata。
- 文档中必须明确：相似性分组来自本地计算，不是 ChromaDB query。

采用 / 不采用结论：

- 采用 metadata 边界和维度一致性要求。
- 不采用 ChromaDB runtime。

#### 记录 7：Pinecone Chunking Strategies

来源名称：Pinecone Chunking Strategies for LLM Applications

来源类型：向量数据库 / RAG 工程文章

链接或出处：`https://www.pinecone.io/learn/chunking-strategies/`

调研问题：

- embedding 输入文本应该多长、包含哪些上下文？
- 输入片段是否需要语义上自洽？

核心做法：

- 文本需要先被切分成有语义意义的 chunk，再 embedding。
- 如果 chunk 太小或太大，会影响检索效果。
- 一个实用原则是：如果这个文本片段离开上下文后人类仍能理解，模型也更可能理解。
- 语义 chunking 可以根据主题变化切分。

可借鉴点：

- V1-B 每个 input 的 embedding text 应该是一个短而自洽的 summary。
- 图片 placeholder 阶段，不能只 embed 空 file url，应组合 title、description、feature summary。
- 文本输入应优先使用 `contentText`，必要时补 title / description。

不能照搬点：

- 本轮不是 RAG，不需要复杂 chunking pipeline。
- 输入是 3-10 个用户样本，不是长文档库。

对 V1-B 的影响：

- 设计 `embedding text builder`：
  - text：`title + contentText + description + feature summary`
  - image：`title + description + placeholder / feature summary`
  - 空文本禁止 embedding。

采用 / 不采用结论：

- 采用“embedding text 必须语义自洽”的原则。
- 不采用复杂 chunking。

#### 记录 8：LangChain Vector Store Integrations

来源名称：LangChain vector store integrations

来源类型：框架文档

链接或出处：`https://docs.langchain.com/oss/python/integrations/vectorstores`

调研问题：

- embedding model 与 vector store 应如何分层？
- vector store 的统一接口通常暴露哪些能力？

核心做法：

- vector store 存储 embedded data 并执行 similarity search。
- 初始化 vector store 时传入 embedding model。
- 常见接口包括 `add_documents`、`delete`、`similarity_search`。
- 很多 vector store 支持 metadata filtering。
- 相似度度量可能是 cosine、Euclidean distance 或 dot product。

可借鉴点：

- `EmbeddingClient` 和 vector store 应分层，不能混在 workflow step 中。
- V1-B 可以先实现 embedding client 和本地 similarity；真实 vector store 留到后续。
- metadata filtering 是后续能力，不属于本轮。

不能照搬点：

- 本轮不引入 LangChain。
- 不把当前小样本分组改造成 RAG retrieval。

对 V1-B 的影响：

- 保持 `EmbeddingClient`、`write_vectors`、`cluster_inputs` 的职责分离。

采用 / 不采用结论：

- 采用分层思想。
- 不采用 LangChain runtime。

### 5.4 调研结论与可借鉴模式

本轮可采用：

- `EmbeddingClient` 抽象，隔离 mock 和未来真实 embedding provider。
- embedding text builder，保证每个 input 的 embedding 文本短而自洽。
- cosine similarity，作为本地 pairwise similarity 的最小实现。
- threshold graph / connected components，用于 3-10 个样本的小样本分组。
- feature overlap，用于生成 `commonFeatures`，避免只凭向量黑盒解释。
- uncertainty 文案，明确样本少、mock embedding、阈值初始值和非绝对聚类结论。
- ChromaDB 只保留 metadata 边界，不做 runtime query。

本轮不采用：

- 真实 OpenAI / Sentence Transformers embedding runtime。
- scikit-learn clustering runtime。
- K-Means。
- DBSCAN / Agglomerative runtime。
- ChromaDB `.add()` / `.query()` runtime。
- LangChain / Pinecone runtime。
- 复杂 RAG chunking pipeline。

### 5.5 可选方案

方案 A：只保留当前 mock group，不使用 embedding。

- 优点：改动最小。
- 问题：不能验证 V1-B 的核心问题。
- 结论：不采用。

方案 B：基于 mock embedding 做 cosine similarity，再用阈值图形成小样本分组。

- 优点：能验证相似度计算和分组 workflow。
- 问题：mock embedding 不代表真实语义效果。
- 结论：采用，作为 V1-B 的主路径。

方案 C：基于 `InputFeature` 的 feature overlap 分组，不使用 embedding。

- 优点：解释性更强。
- 问题：不能验证 embedding 链路。
- 结论：部分采用，只用于生成 `commonFeatures` 和解释，不单独作为分组依据。

方案 D：直接接入真实 embedding API 和 ChromaDB runtime。

- 优点：更接近真实 V1。
- 问题：会扩大到模型配置、成本、runtime 依赖和向量库联调，不适合本轮。
- 结论：本轮不采用。

### 5.6 本轮采用方案

外部调研后采用：

```text
EmbeddingClient 抽象
MockEmbeddingClient 默认保留
embedding text builder 明确规则
cosine similarity 计算
threshold graph / connected components 生成小样本分组
feature overlap 生成 commonFeatures
SimilarityGroup 输出 commonFeatures 和 uncertainty
ChromaDB 继续只记录 metadata 边界
```

设计确认结果：

- embedding text builder 字段优先级已确认。
- 相似度阈值初始值已确认：`0.82`。
- 样本不足策略已确认：少于 3 个不生成 similarity group。
- `commonFeatures` 生成规则已确认：优先取 feature key/value overlap。

## 6. 设计确认

当前状态：

```text
confirmed
```

本节把外部调研结论落成 V1-B 可执行设计。完成本节后，V1-B 可以进入代码实现。

### 6.1 Embedding Text Builder 字段优先级

设计目标：

```text
为每个 input 生成短而自洽的 embedding text，避免空字符串、纯 fileUrl 或不可解释 metadata 进入 embedding。
```

文本输入字段优先级：

1. `title`
2. `contentText`
3. `description`
4. `InputFeature.lowLevelFeatures` summary
5. `InputFeature.sampleEvidence`

文本拼接规则：

```text
标题：{title}
正文：{contentText}
描述：{description}
特征：{feature_key}={value}; ...
证据：{sampleEvidence}
```

图片输入字段优先级：

1. `title`
2. `description`
3. `InputFeature.lowLevelFeatures` summary
4. `InputFeature.sampleEvidence`
5. `fileUrl` 只作为最后占位引用，不作为主要语义内容

图片 placeholder 阶段拼接规则：

```text
标题：{title}
描述：{description}
当前边界：图片真实分析尚未接入，本轮仅使用用户提供的标题、描述和已抽取 placeholder feature。
特征：{feature_key}={value}; ...
证据：{sampleEvidence}
```

空文本处理：

- 如果拼接结果为空，不能调用 `EmbeddingClient`。
- 当前 input 应跳过 embedding，并进入分组 uncertainty。
- 不用 `inputId` 单独充当语义 embedding text。

长度策略：

- 本轮不做复杂 chunking。
- 每个 input 只生成一个 embedding text。
- 如果文本过长，先截取到一个短 summary 范围，后续真实模型接入时再按 token limit 调整。

### 6.2 相似度计算设计

采用算法：

```text
cosine similarity
```

输出范围：

```text
-1 到 1
```

解释规则：

- `1` 表示方向完全一致。
- `0` 表示没有明显方向相似。
- 小于 `0` 表示方向相反或弱相关。
- 本轮 mock embedding 下，分数只用于 workflow 验证，不解释为真实语义强度。

异常规则：

- 空向量：抛出结构化错误或跳过并记录 uncertainty。
- 维度不一致：抛出结构化错误。
- 全零向量：不能参与 cosine similarity。

实现约束：

- 不新增 scikit-learn 依赖。
- 使用轻量 Python helper。
- 单元测试覆盖相同向量、正交向量、空向量、维度不一致。

### 6.3 相似度阈值

初始阈值：

```text
0.82
```

采用原因：

- V1-B 是小样本分组，宁可少分组，也不要过度合并。
- mock embedding 语义可信度有限，阈值不应过低。
- 分组结果需要保持“观察到的相似结构”，而不是绝对聚类。

阈值使用方式：

- 两个 input 的 similarity >= `0.82` 时建立相似边。
- 基于相似边构造 connected components。
- component size >= 2 时生成一个 `SimilarityGroup`。
- 没有满足阈值的边时，不强行生成相似组，可输出空组或弱 uncertainty。

后续可调整：

- 如果手动验收发现过度分组，阈值提高到 `0.86`。
- 如果完全无法形成组，阈值可降到 `0.78`，但必须记录原因。

### 6.4 样本不足策略

输入少于 3 个：

```text
不生成 similarity group。
```

原因：

- MVP 规则建议至少 3 个样本。
- 少于 3 个时，相似性结构缺乏稳定性。

输出策略：

- `similarityGroups` 返回空数组。
- report / downstream interpretation 如果需要说明，使用 uncertainty 文案：

```text
样本数量不足，本轮不生成相似性分组。当前结果只表示单个输入的可观察特征，不代表稳定偏好。
```

输入等于 3 个：

- 可以生成分组，但 uncertainty 必须强调样本较少。

输入大于 3 个：

- 按阈值图生成 groups。
- 每组仍必须包含 uncertainty。

### 6.5 CommonFeatures 生成规则

来源：

```text
InputFeature.lowLevelFeatures
```

生成规则：

1. 对 group 内每个 input 取 `lowLevelFeatures`。
2. 优先找相同 feature key 且相同 value 的交集。
3. 如果没有 key/value 完全一致，则找相同 feature key 的交集。
4. `commonFeatures` 最多保留 3-5 个。
5. 不使用没有 evidence 的 feature。

输出格式：

```text
{feature_key}:{value}
```

示例：

```text
saturation:low
narrativeDensity:low
subjectDistance:distant
```

fallback 策略：

- 如果没有可解释交集，则使用：

```text
commonFeatures: ["weak_shared_structure"]
```

- 同时 uncertainty 必须说明：

```text
该组主要由 embedding 相似度形成，当前可解释共同特征较弱，需要更多样本确认。
```

禁止：

- 不生成“高级”“孤独”“治愈感人格”等无证据标签。
- 不把 `commonFeatures` 写成心理诊断。
- 不用 embedding distance 直接反推出审美概念。

### 6.6 SimilarityGroup 命名与 Uncertainty

group name 规则：

- 基于 `commonFeatures` 生成中性名称。
- 示例：`低密度相似组`、`空间意象相似组`、`弱共同结构组`。
- 不使用人格化、玄学化或价值判断名称。

uncertainty 必须包含：

- 样本数量限制。
- mock embedding 限制。
- 阈值分组不是绝对聚类。

默认 uncertainty 模板：

```text
该分组基于当前样本的 embedding 相似度和可解释 feature overlap 生成。样本数量较少，且当前仍使用 mock embedding，因此它只表示本次输入中的相似结构，不代表长期偏好或绝对分类。
```

### 6.7 最终实现顺序

1. 定义 `EmbeddingClient` 抽象。
2. 调整 `MockEmbeddingClient` 对齐抽象。
3. 新增 embedding text builder。
4. 修改 `generate_embeddings` 支持 client 注入和空文本处理。
5. 新增 cosine similarity helper。
6. 新增 threshold graph / connected components group builder。
7. 修改 `cluster_inputs` 接收 features 和 embeddings。
8. 保持 report API 路径和 response shape 不变。
9. 补单元测试和 workflow 集成测试。
10. 更新 V1-B 执行记录和验收结果。

## 7. 系统边界

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

## 8. 架构设计

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

本轮调用关系：

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

## 9. 模块契约

### 9.1 EmbeddingClient

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

### 9.2 Similarity Calculator

模块职责：

- 计算两个 embedding vector 的相似度。

输入：

- 两个同维度非空向量。

输出：

- `-1` 到 `1` 区间内的 similarity score。

异常情况：

- 空向量。
- 维度不一致。

不涉及：

- 不访问 ChromaDB。
- 不保存业务数据。

### 9.3 Similarity Group Builder

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

## 10. 实现范围

### 10.1 EmbeddingClient 抽象

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

### 10.2 Embedding 输入文本构造

本轮需要明确 embedding 的输入来源。

最低要求：

- 文本输入优先使用 `contentText`。
- 图片输入在真实图片分析前，使用 `title`、`description` 或 feature summary 构造 embedding text。
- 不把空字符串送入 embedding client。
- 每个 input 都能生成 embedding 或被明确跳过并记录原因。

### 10.3 相似度计算

本轮需要新增基础相似度计算能力。

最低要求：

- 使用 cosine similarity 或等价稳定算法。
- 输入向量维度不一致时能识别错误。
- 空向量不能参与相似度计算。
- 相似度计算不依赖 ChromaDB runtime。

### 10.4 小样本相似性分组

本轮需要让 `cluster_inputs` 不再只按固定 mock 分组。

最低要求：

- 输入少于 3 个时可以跳过分组或输出明确 uncertainty。
- 相似输入可以进入同一组。
- 每组包含 `inputIds`、`commonFeatures`、`uncertainty`。
- 分组描述不能被写成绝对聚类结论。
- 分组可以先基于 mock embedding + feature overlap，不要求真实机器学习聚类。

### 10.5 Schema 与输出边界

本轮不新增复杂 schema，优先复用：

- `EmbeddingRecord`
- `SimilarityGroup`

如需补充字段，必须同步：

- 后端 Pydantic schema。
- 前端 TypeScript type。
- `docs/10-Prompt Contract 与结构化输出规范.md` 或对应设计文档。

## 11. 不允许 AI 自行决定的内容

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

## 12. 预期涉及文件

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

## 13. 验收标准

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

## 14. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如有接口或 schema 变化，更新对应设计文档。

当前完成记录：

```text
已完成：
- EmbeddingClient 抽象。
- MockEmbeddingClient 默认保留。
- embedding text builder。
- generate_embeddings 支持 feature-aware text 和 client 注入。
- write_vectors 使用同一个 embedding client 的 modelName。
- cosine similarity helper。
- threshold graph / connected components 小样本分组。
- feature overlap 生成 commonFeatures。
- cluster_inputs 接收 features 和 embeddings。
- workflow 已接入 V1-B 分组逻辑。
- 单元测试覆盖 embedding text、空文本跳过、cosine similarity 异常、threshold 分组、样本不足。
- 集成测试覆盖 workflow 保存 embedding metadata 和 similarity group。

未完成：
- 真实 embedding API。
- ChromaDB runtime 写入和 query。
- 大规模聚类。
- 历史输入检索。
```

验证记录：

```text
2026-06-16：
- backend：python -m pytest，10 passed, 3 warnings。
- frontend：npm run build，通过。
- lints：无新增错误。

2026-06-16 手动验收：
- 用户已完成 V1-B 手动验收。
- 报告仍可生成并展示相似性分组。
- 相似性分组表达未被包装为绝对聚类结论。
- 当前仍接受 mock embedding 边界，不判断真实语义效果。
```

验收结论：

```text
V1-B 通过验收。

已确认：
- EmbeddingClient 抽象和注入边界可用。
- embedding text builder 可为文本和图片 placeholder 构造语义文本。
- cosine similarity 和 threshold graph / connected components 分组逻辑已接入 workflow。
- commonFeatures 来自可解释 feature overlap。
- 样本不足时可以跳过 similarity group。
- 报告链路、反馈链路和现有 API 行为未被破坏。

保留风险：
- 当前 embedding 仍是 mock，不代表真实语义相似度。
- ChromaDB 仍是 metadata 边界，没有 runtime add/query。
- 相似度阈值 0.82 是初始工程阈值，后续可根据样本观察调整。
```

## 15. 下一轮入口

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
