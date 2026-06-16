# AI 审美形成系统：AI Workflow 编排与任务执行文档

## 1. 文档目的

这份文档定义 AI 审美形成系统中一次完整分析任务的执行流程。

它解决的问题是：

> 模块已经定义好了，但系统到底如何按顺序调用、如何处理失败、如何记录日志、哪些步骤可以重试、哪些步骤可以异步执行。

这份文档是 FastAPI 后端实现分析任务编排时的主要依据。

## 2. Workflow 总览

MVP 阶段采用固定 workflow，不需要一开始实现完整 Agent。

```text
createAnalysisJob()
↓
loadInputs()
↓
saveRawInputMetadata()
↓
extractLowLevelFeatures()
↓
generateEmbeddings()
↓
writeVectorsToChromaDB()
↓
groupInputsBySimilarity()
↓
generatePossibleInterpretations()
↓
generateReport()
↓
saveReportAndInsights()
↓
updateJobStatus()
↓
collectFeedback()
↓
updateUserProfile()  // V2，可异步
```

MVP 必须完成到 `collectFeedback()`。`updateUserProfile()` 属于 V2 的轻量画像能力，第一版可以只保存反馈，不立刻更新画像。

后续进阶阶段可以把其中的步骤封装为 Function Calling tools，由 workflow orchestrator 或 Agent 动态选择调用。

## 3. Workflow 基本信息

```json
{
  "workflowId": "aesthetic_analysis_v1",
  "entrypoint": "POST /api/analysis-jobs",
  "runtime": "FastAPI backend",
  "businessDatabase": "PostgreSQL",
  "vectorDatabase": "ChromaDB",
  "statusTable": "analysis_jobs",
  "logTable": "analysis_logs"
}
```

## 4. Job 状态机

分析任务状态建议使用以下枚举：

```text
created
queued
running
feature_extracting
embedding_generating
vector_writing
similarity_grouping
interpreting
report_generating
completed
failed
partial_failed
cancelled
```

状态流转：

```text
created
↓
queued
↓
running
↓
feature_extracting
↓
embedding_generating
↓
vector_writing
↓
similarity_grouping
↓
interpreting
↓
report_generating
↓
completed
```

失败状态：

```text
任意步骤
↓
failed 或 partial_failed
```

## 5. Workflow Step Contract

每个 workflow step 必须定义：

- stepId
- 输入来源
- 输出去向
- 是否异步
- 是否可重试
- 是否允许部分失败
- timeout
- 成本记录
- observability log

## 6. Step 1：创建分析任务

### Step ID

`create_analysis_job`

### 触发方式

前端调用：

```text
POST /api/analysis-jobs
```

### 输入来源

- `userId`
- `inputIds`
- 分析配置

### 输出去向

- PostgreSQL：`analysis_jobs`

### 是否异步

创建 job 本身同步，后续分析流程异步。

### 是否可重试

不可自动重试。重复提交可能创建重复任务，需要前端或后端做幂等控制。

### timeout

3 秒。

### observability log

记录：

- jobId
- userId
- inputIds
- createdAt
- workflowId

## 7. Step 2：加载输入

### Step ID

`load_inputs`

### 输入来源

- PostgreSQL：`aesthetic_inputs`
- 本地文件存储或对象存储

### 输出去向

- workflow memory
- `analysis_logs`

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。某个输入文件读取失败时，可以跳过该输入，但必须记录 `partial_failed`。

### timeout

10 秒。

### 失败处理

如果全部输入加载失败：

```json
{
  "status": "failed",
  "failedStep": "load_inputs",
  "errorType": "INPUT_NOT_FOUND"
}
```

## 8. Step 3：底层特征提取

### Step ID

`extract_low_level_features`

### 输入来源

- workflow memory 中的图片和文本输入
- `10-Prompt Contract 与结构化输出规范.md`

### 输出去向

- PostgreSQL：`input_features`
- `analysis_logs`

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。图片失败不应阻断文本分析，文本失败也不应阻断图片分析。

### timeout

- 单张图片：30 秒。
- 单段文本：20 秒。
- 单个 job 总时间：120 秒。

### 成本记录

记录：

- modelName
- promptVersion
- tokenInput
- tokenOutput
- latencyMs
- estimatedCost

### observability log

记录：

- inputId
- featureType
- promptVersion
- modelName
- schemaValidationResult
- evidenceCount
- uncertaintyCount

### 失败处理

如果 LLM 输出 JSON 解析失败，可以重试一次。

如果违反安全边界，不重试，直接记录为 `POLICY_VIOLATION`。

## 9. Step 4：生成 Embedding

### Step ID

`generate_embeddings`

### 输入来源

- PostgreSQL：`input_features`
- 原始文本摘要
- 图片特征摘要

### 输出去向

- workflow memory
- ChromaDB 待写入数据
- PostgreSQL 可保存 embedding metadata，不建议保存大向量本体

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。某个输入 embedding 失败时，该输入不参与后续分组。

### timeout

60 秒。

### observability log

记录：

- inputId
- embeddingModel
- vectorDimension
- latencyMs
- success

## 10. Step 5：写入 ChromaDB

### Step ID

`write_vectors_to_chromadb`

### 输入来源

- workflow memory 中的 embedding
- metadata：userId、inputId、jobId、feature summary

### 输出去向

- ChromaDB collection：`inputs`

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。失败的向量必须记录，不能静默丢弃。

### timeout

30 秒。

### ChromaDB metadata 示例

```json
{
  "userId": "user_001",
  "inputId": "input_001",
  "jobId": "job_001",
  "inputType": "image",
  "createdAt": "2026-05-15T00:00:00Z"
}
```

## 11. Step 6：相似性分组与共性分析

### Step ID

`cluster_inputs`

### 输入来源

- 当前 job 的 embedding
- ChromaDB 相似输入检索结果
- PostgreSQL 历史报告摘要

### 输出去向

- workflow memory
- PostgreSQL：可保存到 `analysis_results` 或报告相关 JSON 字段

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。如果样本不足，跳过分组，输出 `insufficient_samples`。

### timeout

30 秒。

### 输出要求

```json
{
  "clusters": [],
  "globalPatterns": [],
  "outliers": [],
  "insufficientSamples": false
}
```

## 12. Step 7：生成动态解释候选

### Step ID

`generate_possible_interpretations`

### 输入来源

- 底层特征
- 相似性分组结果
- 用户历史反馈
- `interpretations.generate.v1` prompt contract

### 输出去向

- PostgreSQL：`possible_interpretations`
- `analysis_logs`

### 是否异步

是。

### 是否可重试

可重试一次。

### 是否允许部分失败

不建议部分失败。该步骤失败时，报告可以降级为“观察报告”，但不能生成高层解释。

### timeout

60 秒。

### 必须校验

- 至少 2 条解释候选。
- 每条解释必须有 evidenceRefs。
- 每条解释必须有 uncertainty。
- 不得出现人格诊断或玄学表达。

## 13. Step 8：生成报告

### Step ID

`generate_report`

### 输入来源

- 特征摘要
- 相似性分组摘要
- possible_interpretations
- 用户反馈历史
- `report.generate.v1` prompt contract

### 输出去向

- PostgreSQL：`reports`
- PostgreSQL：`insights`
- ChromaDB collection：`reports`，可在报告保存后写入

### 是否异步

是。

### 是否可重试

可重试一次。

### 是否允许部分失败

不允许。如果报告生成失败，job 状态为 `failed` 或 `partial_failed`。

### timeout

90 秒。

### 输出要求

报告必须包含：

- summary
- observation sections
- interpretation sections
- alternative interpretations
- evidenceRefs
- disclaimer

## 14. Step 9：保存报告和洞察

### Step ID

`save_report_and_insights`

### 输入来源

- report JSON
- insights JSON

### 输出去向

- PostgreSQL：`reports`
- PostgreSQL：`insights`
- ChromaDB collection：`reports`

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。PostgreSQL 保存成功但 ChromaDB 写入失败时，报告仍可展示，但需要记录向量写入失败。

### timeout

20 秒。

## 15. Step 10：收集反馈

### Step ID

`collect_feedback`

### 触发方式

前端调用：

```text
POST /api/insights/{insightId}/feedback
```

### 输入来源

- insightId
- userId
- rating
- feedbackText

### 输出去向

- PostgreSQL：`insight_feedback`

### 是否异步

反馈保存同步，画像更新可异步。

### 是否可重试

可重试。

### timeout

5 秒。

## 16. Step 11：更新用户画像

### Step ID

`update_user_profile`

### 输入来源

- 用户历史报告
- 用户反馈
- 当前报告
- `profile.update.v1` prompt contract

### 输出去向

- PostgreSQL：`user_profiles`、`profile_items`、`profile_evidence`
- ChromaDB：V2 不作为业务记忆来源，后续只服务 personalized retrieval

### 是否异步

是。

### 是否可重试

可重试。

### 是否允许部分失败

允许。画像更新失败不影响报告展示。

### timeout

60 秒。

## 17. API 与 Workflow 对应关系

```text
POST /api/inputs
  -> 保存输入

POST /api/analysis-jobs
  -> create_analysis_job
  -> enqueue workflow

GET /api/analysis-jobs/{jobId}
  -> 查询 job 状态

GET /api/reports/{reportId}
  -> 查询报告

POST /api/insights/{insightId}/feedback
  -> collect_feedback
  -> enqueue update_user_profile
```

## 18. 重试策略

默认重试策略：

```json
{
  "maxRetries": 1,
  "retryDelaySeconds": 3,
  "retryableErrors": [
    "TIMEOUT",
    "INVALID_JSON",
    "MODEL_TEMPORARY_ERROR",
    "VECTOR_DB_TEMPORARY_ERROR"
  ],
  "nonRetryableErrors": [
    "POLICY_VIOLATION",
    "INPUT_NOT_FOUND",
    "SCHEMA_INCOMPATIBLE"
  ]
}
```

## 19. 日志规范

每个 step 都必须写入 `analysis_logs`。

日志字段建议：

```json
{
  "logId": "log_001",
  "jobId": "job_001",
  "stepId": "extract_low_level_features",
  "status": "success",
  "startedAt": "2026-05-15T00:00:00Z",
  "finishedAt": "2026-05-15T00:00:03Z",
  "latencyMs": 3000,
  "inputRef": {},
  "outputRef": {},
  "promptVersion": "image_features.extract.v1",
  "modelName": "mock-model",
  "errorType": null,
  "errorMessage": null
}
```

## 20. MVP 实现建议

第一版可以不引入复杂任务队列，先使用 FastAPI 的 `BackgroundTasks` 或简单异步 service 跑通。

推荐演进顺序：

1. 同步 API + mock service。
2. FastAPI `BackgroundTasks`。
3. 独立 worker。
4. Celery / RQ / Dramatiq 等任务队列。
5. Agent workflow 编排。

MVP 不要求一步到位，但代码结构必须为异步任务预留边界。

## 21. 开发提示

后续让 AI 编写 workflow 代码时，可以使用以下约束：

```text
请根据 `09-AI Workflow 编排与任务执行文档.md` 实现 aesthetic_analysis_v1 workflow。

要求：
1. 每个 step 独立成 service 函数。
2. 不允许把所有逻辑堆在 FastAPI route 中。
3. 每个 step 必须写 analysis_logs。
4. LLM 输出必须先通过 `10-Prompt Contract 与结构化输出规范.md` 中的 schema 校验。
5. PostgreSQL 负责业务数据，ChromaDB 负责向量数据，不要混用职责。
6. 失败时更新 analysis_jobs 状态，并返回可查询的错误信息。
```





