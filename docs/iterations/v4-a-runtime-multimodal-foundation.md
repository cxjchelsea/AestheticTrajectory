# V4-A：Runtime & Multimodal Foundation

当前状态：

```text
implementation_completed / pending_validation
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V3 Personalized Retrieval / RAG / Evaluation baseline 之上，建立 V4 的 **runtime 与多模态地基**：

```text
可配置的真实 / mock AI runtime 边界
↓
图片文件存储与读取（最小路径）
↓
ChromaDB 向量写入与查询（input vectors 起步）
↓
多模态输入 schema 扩展（music / video metadata-only 占位）
↓
workflow / debug 中诚实标记 runtime 来源
```

本轮完成后，用户应能：

- 在配置真实 API key 时使用真实 embedding（可选 LLM feature path）。
- 上传图片文件并由后端持久化（非仅 fileUrl 字符串占位）。
- 在 database 模式下将 input vectors 写入 ChromaDB，并可做最小相似度查询验证。
- 创建 music / video metadata 输入并进入统一 workflow（诚实标注未做内容解析）。

## 2. 上游版本决策

引用 `docs/iterations/v4-0-long-term-personalized-agent-research.md` 已确认决策：

- V4-A 先于 Agent、MCP、知识图谱、审美时间轴。
- 未配置 real runtime 时保持 mock，且 debug panel 必须可见。
- 多模态第一版允许 metadata-only；不得假装已做音视频内容理解。
- history / knowledge / 未来 external context **不进入** profile positive evidence（见 `19-记忆与用户模型设计文档.md`）。
- ChromaDB 先从 input vectors 开始，不索引 knowledge / history 全文。
- 核心事实失败仍 fail-fast；非核心检索可显性降级（按 `13` 与项目 skill 治理规则）。

## 3. 本轮解决什么问题

本轮解决：

```text
如何把 V1–V3 的 mock / heuristic / placeholder 边界升级为可替换的真实 runtime，并扩展多模态输入 schema，而不破坏 evidence-first 与 governance？
```

本轮不解决：

- 审美时间轴 UI/API（V4-B）。
- 知识图谱与外部 RAG runtime（V4-C）。
- Agent / MCP（V4-D）。
- grouping stability / failure replay 完整实现（V4-E）。
- 音乐/视频真实内容解析（ffmpeg、音频特征、视频帧分析等）。
- 生产级 LangSmith / OpenTelemetry pipeline。

## 4. 当前实现快照（V4-A 起点）

| 能力 | 当前状态 |
| --- | --- |
| Feature extraction | `MockFeatureExtractor` 默认；`FeatureExtractor` 接口已存在 |
| Embedding | `MockEmbeddingClient` 默认；`EmbeddingClient` 接口已存在 |
| LLM report generation | workflow 内 heuristic / mock 路径 |
| `write_vectors` | 只写 `EmbeddingRecord` metadata 到 DB/memory，**未**写入 ChromaDB |
| 图片 | `fileUrl` 字符串；`UPLOAD_DIR` 配置存在，无完整上传 API |
| Input types | `image` \| `text` only（`CreateInputRequest`） |
| ChromaDB | `settings.chroma_collection_inputs` 命名占位 |

## 5. 外部调研与方案选择

调研层级：

```text
版本级：引用 v4-0 §6、§9.1
能力级：runtime adapter、file storage、ChromaDB minimal、multimodal schema
实现级：env 切换、shadow mode、migration、测试策略（本节待 V4-A 实现前补全）
```

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| Runtime 切换 | 采用 `EMBEDDING_RUNTIME=mock\|openai`；**不做** shadow compare（V4-A 范围外） |
| Embedding 维度 | mock=8 与 real=512 **分 collection**；禁止混维度写入同一 collection |
| 未配置 API key | `EMBEDDING_RUNTIME=openai` 且无 key → **fail-fast**；默认 `mock` 保持 V3 兼容 |
| 图片存储 | 本地 `UPLOAD_DIR` + `POST /api/files/upload`；**不新增** `input_files` 表，复用 `inputs.file_url` |
| ChromaDB | `HttpClient`（`CHROMA_HOST`/`PORT`）为主；测试用 in-memory fake / 可选 embedded |
| 多模态 schema | 扩展 `InputType` 为 `music` \| `video`；复用 title/description/contentText/fileUrl/source |
| Feature / LLM | V4-A **不接**真实 vision/LLM report；music/video 走 metadata + heuristic/mock features |

### 5.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：ChromaDB upsert 与 metadata 边界

来源名称：ChromaDB Update Data / Metadata Schema Validation

来源类型：向量数据库文档 / Cookbook

链接或出处：

- `https://docs.trychroma.com/docs/collections/update-data`
- `https://cookbook.chromadb.dev/strategies/metadata-schema-validation/`

调研问题：

- V4-A 应 `add` 还是 `upsert`？
- metadata 应在哪一层校验？

核心做法：

- `upsert` 适合 job 重跑或同 `chroma_id` 更新。
- Chroma 不强制 schema；应用层用 Pydantic 校验 metadata 再写入。
- metadata 应用 flat 字段：`input_id`、`user_id`、`job_id`、`model_name`、`vector_dimension`。
- query 维度必须与 collection 一致。

对 V4-A 的启发：

- `chroma_id` 继续用 `chroma_{job_id}_{input_id}`，与 `EmbeddingRecord` 对齐。
- 新建 `app/vector_store/chroma_client.py` + `input_vectors.py`（对齐 `08` §4.11）。
- PostgreSQL 仍为业务事实；Chroma 只存向量与检索 metadata。

不能照搬：

- 不把 report/profile 向量写入 V4-A。
- 不用 Chroma metadata 替代 `embedding_records` 表。

采用结论：

```text
write_vectors 在持久化 EmbeddingRecord 后调用 collection.upsert；metadata 经 Pydantic 校验。
```

#### 记录 2：Chroma 客户端模式（Http vs Embedded）

来源名称：Chroma Client API / V1-B 历史调研

来源类型：文档 / 项目 iteration

链接或出处：

- `https://docs.trychroma.com/docs/collections/add-data`
- `docs/iterations/v1-b-embedding-similarity.md` §记录 6
- `backend/.env.example`（`CHROMA_HOST`/`CHROMA_PORT`）

调研问题：

- 开发环境如何启动 Chroma？
- CI 如何避免依赖外部 Docker？

核心做法：

- 生产/本地开发：`HttpClient(host, port)` 连接独立 Chroma 服务。
- 测试：`ChromaVectorStore` 接口 + fake/in-memory 实现，不强制 CI 起 Docker。
- 单例 client，避免多实例写同一 path（embedded 模式注意事项）。

对 V4-A 的启发：

- 默认 `CHROMA_ENABLED=false`：跳过远程 upsert，仍写 `EmbeddingRecord`（显性降级事件记入 debug）。
- `CHROMA_ENABLED=true` 且 upsert 失败：记录 `fallback_events`，不 silent 成功。
- 人工验收时在本地开启 Chroma 验证 query。

采用结论：

```text
HttpClient 为默认集成路径；CHROMA_ENABLED 控制是否远程写入；测试用 fake store。
```

#### 记录 3：OpenAI text-embedding-3-small

来源名称：OpenAI Embeddings Guide / Embeddings v3

来源类型：API 文档 / 工程文章

链接或出处：

- `https://developers.openai.com/api/docs/guides/embeddings`
- `https://www.pinecone.io/learn/openai-embeddings-v3/`

调研问题：

- 真实 embedding 用哪个模型？
- 与 mock 8 维如何共存？

核心做法：

- `text-embedding-3-small` 默认 1536 维，可通过 `dimensions` 参数截断（如 512）。
- 更换维度 = 不同向量空间；**不能**与 mock 8 维混用同一 collection。
- 未配置 key 时不应静默回退（项目 fail-fast 规则）。

对 V4-A 的启发：

- 新增 `OpenAIEmbeddingClient`，`vector_dimension=512`（平衡存储与语义，可配置）。
- collection 命名：`inputs_{runtime}_{dimension}`，例如 `inputs_mock_8`、`inputs_openai_512`。
- `settings.embedding_model` 记录实际 model name；debug `mockUsage` 区分 mock/openai。

采用结论：

```text
V4-A 接 OpenAI embedding 为 optional real path；mock 仍为默认；分 collection 隔离维度。
```

#### 记录 4：Embedding text 与多模态 metadata-only

来源名称：Pinecone Chunking Strategies / 现有 `build_embedding_text`

来源类型：工程实践 / 项目代码

链接或出处：

- `https://www.pinecone.io/learn/chunking-strategies/`
- `backend/app/workflows/steps/build_embedding_text.py`

调研问题：

- music/video 无内容解析时如何 embed？
- 如何避免空向量？

核心做法：

- 每个 input 的 embedding text 须语义自洽（V1-B 已采纳）。
- metadata-only 模态：组合 title、description、contentText（用户备注）、fileUrl（链接）、source。
- 必须包含显性边界句：「当前未解析音视频内容，仅使用元数据」。

对 V4-A 的启发：

- 扩展 `build_embedding_text` 分支：`music` / `video`。
- `MockFeatureExtractor` / `heuristic` 为 music/video 生成占位 feature（基于 metadata 关键词）。
- 前端表单展示 metadata-only 说明。

采用结论：

```text
不新增 DB 列；扩展 InputType + build_embedding_text + 校验规则即可。
```

#### 记录 5：本地文件上传（FastAPI）

来源名称：FastAPI UploadFile / 项目 `local_storage.py`

来源类型：框架文档 / 项目代码

链接或出处：

- FastAPI `UploadFile` 模式
- `backend/app/storage/local_storage.py`
- `docs/08` §4.12 storage 分层

调研问题：

- 是否需要独立 `input_files` 表？
- 图片如何与 input 关联？

核心做法：

- `POST /api/files/upload` 保存至 `UPLOAD_DIR/{user_id}/{uuid}.{ext}`。
- 返回可访问 `fileUrl`（如 `/api/files/{file_id}` 或相对 path）。
- 创建 image input 时引用返回的 `fileUrl`。
- route 不直接拼路径，走 storage service。

对 V4-A 的启发：

- V4-A **不新增** `input_files` 表；`inputs.file_url` 存服务 URL。
- 增加 MIME/大小校验（如 image ≤ 10MB）。
- 无文件时 image input 仍可走 mock url（开发兼容）。

采用结论：

```text
单文件上传 API + local storage；file_url 关联现有 inputs 表。
```

#### 记录 6：Runtime 切换与 debug 诚实标记

来源名称：项目 AI Governance / `analysis_job_service._mock_usage`

来源类型：项目 skill / 现有 debug 实现

调研问题：

- 用户如何知道当前是 mock 还是 real？

核心做法：

- 已有 `MockUsageRecord` / `mockUsage` in debug API。
- V4-A 扩展为 `runtimeUsage` 或扩充 `mockUsage`：embeddingRuntime、chromaEnabled、storageBackend。

对 V4-A 的启发：

- `EMBEDDING_RUNTIME=openai` 且成功时，`mockUsage` 中 embedding 项标记 `userVisible=false` 并附 `developerMessage` 说明 real model。
- Chroma 跳过或失败写入 `fallback_events`。

采用结论：

```text
扩展现有 debug 语义，不新建生产 dashboard。
```

### 5.3 方案对比

#### 5.3.1 Embedding runtime

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 仅 mock，defer real | 零改动 | 不兑现 V4-A carry_over | 拒绝 |
| B | mock + OpenAI `text-embedding-3-small` dim=512 | 可配置、成本可控 | 需 API key；维度与 mock 分离 | **采用** |
| C | 本地 sentence-transformers | 无 API 成本 | 新依赖、部署复杂 | V4-A 拒绝，可 V4+ 评估 |

#### 5.3.2 ChromaDB 部署

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 仅 PostgreSQL metadata，不写 Chroma | 测试简单 | 不兑现 V4-A | 拒绝 |
| B | HttpClient + CHROMA_ENABLED 开关 | 与 `.env.example` 一致 | 需本地 Chroma 服务做人工验收 | **采用** |
| C | 强制 Embedded PersistentClient | 无 Docker | 与 08 目录规划、并发写 path 风险 | 仅作 dev 备选 |

#### 5.3.3 图片存储

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 继续 mock:// url | 无后端改动 | 不兑现 V4-A | 拒绝 |
| B | local `UPLOAD_DIR` + upload API | 简单、可验收 | 非对象存储 | **采用** |
| C | 云对象存储 SDK | 生产级 | 超 V4-A 范围 | 拒绝 |

#### 5.3.4 多模态 schema

| 方案 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A | 新表 `multimodal_inputs` | 结构清晰 | 过度设计 | 拒绝 |
| B | 扩展 `InputType` + 复用现有字段 | 最小 migration | 字段语义靠约定 | **采用** |
| C | JSON blob 存一切 | 灵活 | 难校验、难 UI | 拒绝 |

#### 5.3.5 未配置 real runtime 时行为

| 方案 | 做法 | 结论 |
| --- | --- | --- |
| 默认 `EMBEDDING_RUNTIME=mock` | 与 V3 归档行为一致 | **采用** |
| `EMBEDDING_RUNTIME=openai` 无 key | workflow fail-fast，明确错误 | **采用** |
| 无 key 时 silent 回退 mock | 违反项目治理 | **拒绝** |

### 5.4 最终方案选择

#### 5.4.1 配置项（`.env`）

```text
EMBEDDING_RUNTIME=mock|openai          # 默认 mock
OPENAI_API_KEY=                        # openai 时必填
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=512               # openai path；mock 固定 8
CHROMA_ENABLED=false|true              # 默认 false（CI/memory 友好）
CHROMA_HOST=127.0.0.1
CHROMA_PORT=8001
UPLOAD_DIR=./uploads
MAX_UPLOAD_BYTES=10485760              # 拟：10MB
```

#### 5.4.2 模块与目录

```text
backend/app/ai/factory.py              # get_embedding_client()
backend/app/ai/openai/openai_embedding.py
backend/app/vector_store/chroma_client.py
backend/app/vector_store/input_vectors.py
backend/app/storage/file_storage.py    # save_upload, resolve_url
backend/app/api/routes/files.py        # POST /api/files/upload, GET /api/files/{id}
```

#### 5.4.3 Chroma metadata schema（Pydantic）

```json
{
  "input_id": "string",
  "user_id": "string",
  "job_id": "string",
  "input_type": "image|text|music|video",
  "model_name": "string",
  "vector_dimension": 8
}
```

#### 5.4.4 Collection 命名

```text
{chroma_collection_inputs}_{runtime}_{dimension}
例：inputs_mock_8、inputs_openai_512
```

#### 5.4.5 多模态字段约定（metadata-only）

| type | title | contentText | fileUrl | description | source |
| --- | --- | --- | --- | --- | --- |
| music | 曲名 | 用户备注 | 播放链接 | 艺人/专辑 | manual / link |
| video | 标题 | 用户备注 | 视频链接 | 频道/系列 | manual / link |

校验：music/video 至少提供 title 或 fileUrl 之一；不得声称已解析媒体内容。

#### 5.4.6 workflow 变更

```text
generate_embeddings → 使用 factory client
write_vectors → EmbeddingRecord 持久化 +（CHROMA_ENABLED 时）input_vectors.upsert
extract_features → V4-A 仍默认 MockFeatureExtractor（music/video 增加 metadata heuristic）
```

#### 5.4.7 降级边界

| 场景 | 行为 |
| --- | --- |
| `CHROMA_ENABLED=false` | 跳过 upsert；debug 记录 skipped；EmbeddingRecord 仍写入 |
| `CHROMA_ENABLED=true` 且连接失败 | 记录 fallback_event；job 可完成但 debug 明示 |
| `EMBEDDING_RUNTIME=openai` 无 key | fail-fast，job 失败 |

### 5.5 调研问题（原始清单）

- Runtime 切换：环境变量一次切换 mock/real，还是并行 shadow compare？→ **一次切换，无 shadow**
- 真实 embedding 供应商与维度？→ **OpenAI text-embedding-3-small, dimensions=512**
- 图片存储与表结构？→ **local upload API，复用 file_url**
- ChromaDB 部署？→ **HttpClient + CHROMA_ENABLED**
- 多模态 schema？→ **扩展 InputType，metadata-only**
- 未配置 API key？→ **openai 模式 fail-fast；默认 mock**

## 6. 系统边界

### 6.1 必做

- [ ] 可配置 embedding runtime（mock + 至少一条 real path 或明确 deferred 原因）。
- [ ] 图片文件上传与持久化读取最小 API。
- [ ] ChromaDB input collection 写入与最小查询验证。
- [ ] 扩展 `InputType`：`music`、`video`（metadata-only）。
- [ ] workflow / debug 标记 `mockUsage` / runtime source（扩展现有 debug 语义）。
- [ ] 单元测试 + 集成测试覆盖 mock 与（可选）real 配置路径。
- [ ] 人工验收清单（§10）。

### 6.2 不做

- [ ] Agent、MCP、知识图谱。
- [ ] 审美时间轴。
- [ ] 外部 RAG 向量库。
- [ ] 音视频内容解析。
- [ ] 把新模态输入直接写入 profile 无 feedback 路径。

## 7. 架构影响

### 7.1 后端

- `app/core/config.py`：runtime、Chroma、storage 相关配置。
- `app/ai/`：real embedding /（可选）LLM client 实现。
- `app/workflows/steps/write_vectors.py`：实际 Chroma upsert。
- 新增或扩展：file upload route、Chroma client 封装、multimodal input validation。
- `analysis_job_service.get_debug`：扩展 runtime / chroma / storage trace（若需要）。

### 7.2 前端

- 图片上传组件（若当前仅 text/url）。
- music / video metadata 表单（明确「仅元数据」文案）。
- 开发环境 debug 展示 runtime / mock 标记（可选增强）。

### 7.3 数据

- 可能扩展 `inputs` 类型枚举与字段（见 `07`，实现前上升）。
- 可能新增 `input_files` 或等价 metadata（实现前确认）。
- `embedding_records` 与 Chroma 一致性约束。

### 7.4 权威设计文档更新判断

```text
V4-A 方案确认后更新：
- docs/07（input schema、Chroma runtime、文件存储）
- docs/11（runtime adapter、upload、chroma 模块）
- docs/20-多模态偏好建模设计文档.md（拟，按 agent-frontier-design-docs 登记表创建）
实现前本文档保持 planned；确认后记录 "Authoritative design doc update required"。
```

## 8. 模块契约（草案）

### 8.1 Runtime adapter 模块

- 输入：配置 + input/features
- 输出：features / embeddings /（可选）LLM 结构化片段
- 错误：未配置 key 时按治理规则 fail-fast 或显性 mock
- 测试：mock 默认路径；real 路径可选 integration（需 env）

### 8.2 File storage 模块

- 输入：multipart upload 或 base64（择一）
- 输出：持久化 path / url + input 关联
- 权限：同 user scope（匿名体系下与现有一致）

### 8.3 Chroma vector 模块

- 输入：embedding vector + metadata（input_id, job_id, user_id）
- 输出：chroma_id 与 query results
- 边界：仅 input vectors；不写 report/profile

### 8.4 Multimodal input 模块

- 输入：music / video metadata
- 输出：`AestheticInputResponse` 进入现有 workflow
- UI：标注 metadata-only

## 9. API 设计（方案确认）

| API | Method | 说明 |
| --- | --- | --- |
| `POST /api/files/upload` | multipart | 保存图片；返回 `{ fileId, fileUrl, mimeType, sizeBytes }` |
| `GET /api/files/{file_id}` | GET | 读取已上传文件（同 user scope 规则） |
| `POST /api/inputs` | JSON | 扩展 `type`: `music` \| `video`；校验 metadata-only 规则 |
| `GET /api/analysis-jobs/{job_id}/debug` | GET | 扩展 runtime/chroma/storage trace（可选） |

`POST /api/inputs` 对 image 可继续只传 `fileUrl`（由 upload API 产生）。

## 10. 验收标准

### 10.1 自动验证

- memory backend 全量 pytest 仍通过（或明确新增测试覆盖）。
- database backend：embedding record + Chroma metadata 一致性测试。
- mock 路径：行为与 V3 归档基线兼容（无静默退化）。
- multimodal：music/video input 可创建并进入 workflow。

### 10.2 人工验证

- 配置 mock：分析流程与 V3 一致，debug 显示 mock。
- 配置 real embedding（若有 key）：新分析写入 Chroma，可查相似 input。
- 图片上传：报告可关联真实文件路径/URL。
- music/video 表单：显示 metadata-only 说明；报告不声称已解析音视频内容。
- profile / history / knowledge 边界：V3-E 治理测试仍通过。

### 10.3 人工验收清单

- [x] mock 默认：完整分析路径与 V3 一致。
- [x] 上传图片后 `fileUrl` 指向真实服务端点，可访问。
- [x] `CHROMA_ENABLED=true` 且 Chroma 可用：upsert 成功（collection `inputs_ollama_768`）；query neighbor 待可选补验。
- [ ] `EMBEDDING_RUNTIME=openai` + 有效 key：embedding model 名与维度正确，debug 不声称 mock。（单测覆盖，人工未跑）
- [ ] `EMBEDDING_RUNTIME=openai` 无 key：任务失败，错误信息明确。（单测覆盖，人工未跑）
- [x] music/video 输入进入 workflow，报告/UI 不声称已解析音视频。（场景 C UI 跳过，API/单测通过）
- [x] V3-E governance 测试仍全部通过。

## 11. AI 生成代码顺序（确认）

1. Config + runtime factory / env 边界
2. Chroma client 封装 + write_vectors 实际 upsert
3. File upload API + storage
4. Input schema 扩展（backend + frontend types）
5.（可选）Real embedding client
6. Debug trace 扩展
7. Tests
8. 文档与 `15` 执行记录

1. Config + `get_embedding_client()` factory
2. `ChromaVectorStore` + `input_vectors.upsert` + fake for tests
3. `file_storage` + `POST/GET /api/files`
4. Input schema 扩展（backend + frontend types + validation）
5. `OpenAIEmbeddingClient`
6. `build_embedding_text` music/video 分支
7. `write_vectors` 接入 Chroma + debug/fallback 扩展
8. Tests（unit + integration；Chroma fake 默认）
9. 上升 `07` / `11` / `20`（多模态设计文档）+ `15` 执行记录

## 12. 权威设计文档更新判断

```text
方案已确认，实现开始前应更新：
- docs/07：InputType、Chroma runtime、upload、collection 命名
- docs/11：embedding factory、vector_store、file upload 模块契约
- docs/20-多模态偏好建模设计文档.md（创建，登记 Multimodal Preference Modeling）
实现迭代结束时更新 docs/13 验收项（如有新 governance 检查）。
```

## 13. 用户确认（已接受）

- [x] 是否接受 OpenAI `text-embedding-3-small` + `dimensions=512` 作为 real embedding path。
- [x] 是否接受 mock(8) 与 openai(512) **分 collection**，不迁移历史 mock 向量。
- [x] 是否接受 `CHROMA_ENABLED` 默认 `false`，开启后才远程 upsert。
- [x] 是否接受图片上传走 `POST /api/files/upload`，不新增 `input_files` 表。
- [x] 是否接受 music/video metadata-only，不接内容解析。

## 14. 文档与复盘

- 实现完成后更新：`15` §20、`12` 当前子阶段、`agent-frontier-design-docs.md`（Multimodal → created/partial）。
- 迭代结束记录：命令、测试结果、mock/real 边界截图或说明、遗留到 V4-B 的项。

## 15. 当前结论

```text
V4-A 已验收通过，状态 accepted。
已实现：mock 默认 + OpenAI/Ollama embedding optional + HttpClient Chroma + local upload + metadata-only music/video。
memory backend pytest：64 passed（2026-06-18）。
权威文档已上升：07 §10.8、11 §4.7.1–4.7.2、20。
下一子阶段：V4-B Aesthetic Trajectory & Temporal Profiling。
```
