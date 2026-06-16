# V1-D：数据持久化与基础日志

当前状态：

```text
accepted / archived
```

创建日期：

```text
2026-06-16
```

## 1. 本轮目标

在 V1-A / V1-B / V1-C 已归档的 mock workflow 基线之上，让系统具备真实业务数据持久化和基础 workflow 日志能力，为 V2 历史报告和轻量画像提供可靠事实来源。

本轮目标链路：

```text
AestheticInput
↓
AnalysisJob
↓
InputFeature
↓
EmbeddingRecord metadata
↓
Report / PossibleInterpretation / Insight
↓
InsightFeedback
↓
AnalysisLog
↓
PostgreSQL business source of truth
```

## 2. 当前基线

当前已归档状态：

```text
V1-A accepted / archived
V1-B accepted / archived
V1-C accepted / archived
```

已确认：

- workflow 已能生成 `InputFeature`。
- workflow 已能生成 embedding metadata 和 similarity groups。
- workflow 已能生成动态 report、possible interpretations、insights。
- feedback API 已能保存 insight-level feedback。
- 当前 repository 仍以 `MemoryStore` 为主，重启后数据会丢失。
- 当前 `analysis_logs` 尚未持久记录 step、状态、模型、耗时和错误。

当前限制：

- 未接真实 PostgreSQL runtime。
- 未建立数据库 migration。
- 未建立 PostgreSQL model / repository 实现。
- 未建立持久化 `analysis_logs`。
- ChromaDB runtime 仍暂缓。

## 3. 本轮解决什么问题

本轮解决：

```text
系统能否把输入、特征、任务、报告、洞察、反馈和基础日志持久化，为长期记忆做准备？
```

本轮不解决：

- 历史报告列表。
- 报告对比。
- 轻量用户画像。
- 反馈影响画像权重。
- ChromaDB runtime add/query。
- 独立任务队列。
- OpenTelemetry runtime。
- Agent / MCP / RAG。

## 4. 必须阅读的文档

只需要阅读以下文档：

1. `docs/07-数据结构与系统架构文档.md`
2. `docs/08-项目目录结构与代码分层规范.md`
3. `docs/09-AI Workflow 编排与任务执行文档.md`
4. `docs/10-Prompt Contract 与结构化输出规范.md`
5. `docs/16-V1开发收口清单.md`
6. `docs/12-开发任务拆分与里程碑计划.md`
7. `docs/iterations/v1-a-real-feature-extraction.md`
8. `docs/iterations/v1-b-embedding-similarity.md`
9. `docs/iterations/v1-c-report-feedback.md`

不要一次性读取 `03-16` 全量文档。

## 5. 外部调研与方案选择

本节必须在实现 V1-D 代码前完成。

调研要求：

```text
本轮必须进行外部调研，并在本文档中记录。

不能只基于当前代码和通用工程经验直接设计。
不能只写“通用做法”，必须记录具体来源、可借鉴点、不能照搬点、最终采用 / 不采用理由。
```

### 5.1 调研问题

本轮调研只围绕数据持久化与基础日志：

- FastAPI 后端应如何接 PostgreSQL？
- 本项目应优先使用 SQLAlchemy 还是 SQLModel？
- Alembic migration 应如何管理？
- repository pattern 如何与当前 `MemoryStore` 过渡？
- `analysis_logs` 应记录哪些字段，如何避免日志噪音？
- 是否需要立即接入 structlog / OpenTelemetry？
- 如何保证 workflow 状态更新和日志记录具备基本一致性？

### 5.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：FastAPI + SQLAlchemy + PostgreSQL + Alembic

来源名称：Building a Production-Grade Async Backend with FastAPI, SQLAlchemy, PostgreSQL, and Alembic

来源类型：工程实践文章

链接或出处：`https://dev.to/rosewabere/building-a-production-grade-async-backend-with-fastapi-sqlalchemy-postgresql-and-alembic-2ca4`

调研问题：

- FastAPI 项目如何分层接入 PostgreSQL？
- session、transaction、repository 应如何组织？
- Alembic 在生产项目中的角色是什么？

核心做法：

- routes 只处理 HTTP。
- services 放业务逻辑。
- repositories 负责数据访问。
- db/session 层负责 engine、session lifecycle 和 transaction。
- Alembic 负责 schema evolution。
- async stack 可使用 SQLAlchemy + asyncpg。
- migration 需要导入所有 models，否则 Alembic 无法 autogenerate。

对本项目的启发：

- 符合当前 `08-项目目录结构与代码分层规范.md`。
- V1-D 应新增 `backend/app/db`、`backend/app/models` 和数据库 repository 实现。
- 不应在 route 或 workflow step 中直接写 SQL。
- Alembic 应从第一版表结构就接入，避免用 `create_all` 作为长期方案。

不能照搬：

- 文章偏生产级 async backend，本项目 V1-D 仍是本地开发和 MVP 收口，不需要一次性引入完整部署、连接池调优和复杂事务封装。

采用结论：

```text
采用 SQLAlchemy + PostgreSQL + Alembic 的方向；repository / service / db 分层作为 V1-D 默认架构。
```

#### 记录 2：FastAPI + SQLAlchemy best practices

来源名称：FastAPI + SQLAlchemy Best Practices

来源类型：工程实践文章

链接或出处：`https://mshaeri.com/blog/fastapi-sqlalchemy-best-practices/`

调研问题：

- repository 和 transaction 边界应如何控制？
- migration 应如何保持干净？
- 低层 helper 是否应该 commit？

核心做法：

- 使用 yield dependency 管理 session lifecycle。
- 保持 transaction boundary 显式。
- 低层 helper 不应随意 commit。
- migration 要保持小而清晰。
- 不应修改已经在共享环境使用过的 migration。
- 避免 accidental lazy loading 和 N+1。

对本项目的启发：

- V1-D repository 不应自行决定复杂业务流程。
- workflow 或 service 应掌握一次分析流程的 transaction boundary。
- 第一版 migration 可以作为 V1-D 初始 schema，后续变更再新增 migration。

不能照搬：

- 本项目当前没有真实多用户和高并发读写，不需要立刻优化 N+1、锁策略或复杂查询性能。

采用结论：

```text
采用显式 transaction boundary 和干净 migration 规则；性能优化延后。
```

#### 记录 3：SQLModel + Alembic

来源名称：How to run a database migration when using SQLModel / SQLModel Alembic setup

来源类型：GitHub issue / 社区实践

链接或出处：`https://github.com/fastapi/sqlmodel/issues/85`

调研问题：

- 是否应采用 SQLModel，复用 Pydantic 风格？
- SQLModel 与 Alembic 集成有什么注意事项？

核心做法：

- Alembic `env.py` 需要设置 `target_metadata = SQLModel.metadata`。
- `env.py` 必须导入所有 table models。
- migration template 需要 `import sqlmodel`。
- 推荐用 `python -m alembic revision --autogenerate` 避免 PYTHONPATH 问题。

对本项目的启发：

- SQLModel 对小项目有吸引力，因为 schema 写法接近 Pydantic。
- 但本项目已存在较完整 Pydantic response schema，数据库模型不一定要和 API schema 合并。
- SQLModel + Alembic 有额外配置细节，可能增加初期不确定性。

不能照搬：

- 不应因为 SQLModel 写法简洁就把 API schema 和 database model 合并。
- 不应让 table model 直接替代现有 Pydantic contract。

采用结论：

```text
本轮暂不优先采用 SQLModel。优先采用 SQLAlchemy ORM + Pydantic schemas 分离，保持现有 API contract 稳定。
```

#### 记录 4：Alembic migration best practices

来源名称：Building Production-Ready APIs with FastAPI, SQLAlchemy, and Alembic

来源类型：工程实践文章

链接或出处：`https://pub.towardsai.net/building-production-ready-apis-with-fastapi-sqlalchemy-and-alembic-a-complete-guide-a4656b7e700c`

调研问题：

- migration 应如何生成、应用和维护？
- 增加 NOT NULL 字段时有什么风险？

核心做法：

- 每次 schema 变化生成 migration。
- autogenerate 后必须人工 review。
- 添加 NOT NULL 字段时给已有数据设置 server default 或做分阶段迁移。
- migration 应小而清晰。
- 不编辑已应用 migration。

对本项目的启发：

- V1-D 初始 migration 应只包含 V1 必需业务表。
- 不在同一轮引入 ChromaDB runtime 表外逻辑。
- JSON 字段可用于保存 report / feature / evidence 的结构化快照。

不能照搬：

- 当前没有共享生产数据库，不需要备份、回滚演练和部署流水线，但规则应提前写入。

采用结论：

```text
采用 Alembic 初始 migration；migration 自动生成后必须人工复查，不用 create_all 代替 migration。
```

#### 记录 5：FastAPI structured logging / structlog

来源名称：A complete guide to logging in FastAPI / asgi-correlation-id / structlog practices

来源类型：工程实践文章与开源项目文档

链接或出处：

- `https://apitally.io/blog/fastapi-logging-guide`
- `https://github.com/snok/asgi-correlation-id`

调研问题：

- FastAPI 中如何做结构化日志？
- 是否需要 request id / correlation id？
- 本轮是否应接入 structlog？

核心做法：

- 生产日志应使用 JSON structured logs。
- 日志字段保持一致，便于查询。
- request id / correlation id 贯穿一次请求。
- structlog 可用 contextvars 绑定 request_id。
- 不记录 token、密码或敏感 PII。

对本项目的启发：

- `analysis_logs` 应使用稳定字段：job_id、step_id、status、model_name、prompt_version、latency_ms、error_type、error_message。
- request 层结构化日志和 workflow 业务日志可以分阶段处理。
- V1-D 最关键的是持久化 workflow step logs，而不是完整 production logging stack。

不能照搬：

- 不在 V1-D 引入完整 structlog + correlation-id middleware，除非实现复杂度很低且不影响主链路。
- 不将每条 HTTP access log 都入库。

采用结论：

```text
V1-D 采用数据库 `analysis_logs` 作为主日志目标；structlog / request correlation id 暂缓到可观测性增强阶段。
```

#### 记录 6：OpenTelemetry FastAPI instrumentation

来源名称：OpenTelemetry FastAPI Instrumentation

来源类型：官方/生态文档

链接或出处：`https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html`

调研问题：

- 是否应在 V1-D 接入 OpenTelemetry？
- tracing 与 `analysis_logs` 的边界是什么？

核心做法：

- `FastAPIInstrumentor.instrument_app(app)` 可自动捕获 HTTP traces。
- 可以配置 request / response hooks。
- 可以捕获 headers，但需要注意 sanitize。
- log 与 trace 关联需要 trace_id / span_id。

对本项目的启发：

- OpenTelemetry 适合 V3 之后的系统可观测性和外部服务调用追踪。
- V1-D 只需要解释 workflow 各 step 是否成功、耗时和错误。

不能照搬：

- 当前没有多服务链路、部署 APM 或 tracing 后端，不应为了“看起来完整”引入 OpenTelemetry。

采用结论：

```text
本轮不采用 OpenTelemetry runtime；只保留未来接入的字段意识，例如 step_id、latency_ms、error_type。
```

#### 记录 7：Workflow audit trail / state transition logging

来源名称：Backend Workflow Patterns / Tasker idempotency and atomicity

来源类型：工程实践文档

链接或出处：

- `https://www.xano.com/blog/backend-workflows-best-practices/`
- `https://docs.tasker.systems/architecture/idempotency-and-atomicity.html`

调研问题：

- workflow step logs 应如何支持排错？
- 状态更新和日志记录如何保持一致？
- 是否需要状态机和幂等键？

核心做法：

- workflow 应有显式 status enum。
- 用 dedicated workflow events / logs table 记录状态变化。
- 日志包含 workflow id / step id / status / timestamp / error context。
- 状态更新与日志写入应在明确 transaction boundary 中完成。
- 幂等键和状态机适合更复杂的 job / worker 系统。

对本项目的启发：

- `analysis_jobs` 保存当前任务状态。
- `analysis_logs` 追加记录每个 step 的执行结果。
- V1-D 应优先保证“可查询任务状态”和“可回看 step 失败原因”。
- 当前不需要独立 worker、重试队列、租约或分布式锁。

不能照搬：

- 不实现复杂状态机、幂等任务提交、worker lease、dead-letter queue。

采用结论：

```text
采用 append-style `analysis_logs` 和明确 job status；复杂任务队列与幂等系统延后。
```

#### 记录 8：Audit logging schema practices

来源名称：Data audit trail / audit log schema practices

来源类型：工程实践文章

链接或出处：`https://www.datasunrise.com/knowledge-center/data-audit-trails/`

调研问题：

- 是否需要完整审计日志？
- JSON 快照适不适合 V1-D？

核心做法：

- 审计日志一般 append-only。
- 记录 actor、target object、action、result、timestamp。
- 可用 JSON old/new snapshots 支持灵活调试。
- 应限制日志范围，避免噪音和隐私风险。

对本项目的启发：

- V1-D 的 `analysis_logs` 不是合规审计系统，而是 workflow 可观测日志。
- JSON snapshot 可用于后续增强，但本轮字段先保持克制。
- 不记录用户原始大文本、图片内容、密钥或敏感信息到 logs。

不能照搬：

- 不建立通用 audit_log 触发器系统。
- 不做日志分区、WORM、合规报表。

采用结论：

```text
本轮只实现 scoped workflow logs，不做完整 audit trail。
```

### 5.3 调研结论与可借鉴模式

本轮可采用：

- SQLAlchemy ORM + PostgreSQL。
- PostgreSQL 作为业务数据库的项目级选型依据见 `docs/07-数据结构与系统架构文档.md` 的“为什么选择 PostgreSQL”。
- Alembic migration。
- Pydantic API schema 与 DB model 分离。
- Repository 层承接数据库读写。
- `MemoryStore` 保留为测试 / fallback 边界，不作为生产事实来源。
- `analysis_jobs` 保存当前状态。
- `analysis_logs` append-style 记录每个 workflow step。
- JSON / JSONB 保存 feature、report、evidence 等结构化快照。
- `.env.example` 声明 `DATABASE_URL`。

本轮不采用：

- SQLModel 作为默认 ORM。
- `metadata.create_all` 代替 migration。
- OpenTelemetry runtime。
- 完整 structlog / request correlation id stack。
- 通用 audit trigger 系统。
- 独立 worker / queue / retry / dead-letter。
- ChromaDB runtime add/query。

### 5.4 本轮采用方案

外部调研和现有代码结构复核后采用：

```text
ORM：SQLAlchemy
Migration：Alembic
Database：PostgreSQL
Driver：同步 psycopg
Schema：Pydantic API schema 与 SQLAlchemy DB model 分离
Repository：新增 database repository，与现有 MemoryStore repository 并存
Logs：新增 analysis_logs repository，workflow step 写入 append-style 日志
JSON fields：PostgreSQL 使用 JSONB；SQLite 测试使用 JSON 兼容字段
ChromaDB：继续暂缓 runtime
OpenTelemetry：暂缓
```

设计确认结果：

- 同步 SQLAlchemy + psycopg：已确认。
- 先实现 PostgreSQL runtime，同时保持 SQLite-compatible 测试路径：已确认。
- 初始 migration 包含 V1 必需业务表，并包含 `embedding_records` metadata：已确认。
- repository 通过配置选择 `memory` 或 `database` backend：已确认。
- workflow 每个主要 step 写 `analysis_logs`，失败时记录 error 并更新 job：已确认。
- `analysis_logs` 使用 `started_at` / `finished_at` / `latency_ms`：已确认。
- 测试策略：默认 SQLite repository 测试 + 现有 API / workflow 测试；PostgreSQL runtime 以本地手动验收确认：已确认。

## 6. 系统边界

本轮包含的能力：

- PostgreSQL 连接配置。
- Alembic 初始 migration。
- V1 必需业务表。
- DB model。
- Database repository。
- analysis job / input / feature / embedding metadata / report / interpretation / insight / feedback 持久化。
- `analysis_logs` 基础记录。
- `.env.example`。
- 后端测试。

本轮暂缓的能力：

- ChromaDB runtime。
- 文件真实持久化。
- 历史报告列表 UI。
- 报告详情回看 UI。
- 用户画像更新。
- request-level structured logging。
- OpenTelemetry。
- 独立任务队列。

本轮明确不做：

- V2 历史报告。
- V2 轻量画像。
- V3 personalized retrieval。
- V4 Agent / MCP。
- 多租户权限系统。
- 完整登录系统。

边界原因：

```text
V1-D 只负责把当前 V1 workflow 的业务事实和基础 step logs 落到持久化层，不负责长期记忆推理。
```

## 7. 设计确认

当前状态：

```text
confirmed
```

本节把外部调研结论和当前代码结构落成 V1-D 可执行设计。完成本节后，V1-D 可以进入代码实现。

### 7.1 SQLAlchemy Sync / Async 选择

本轮采用：

```text
SQLAlchemy sync ORM + psycopg
```

原因：

- 当前 FastAPI service、repository 和 workflow 全部是同步函数。
- 当前依赖只有 FastAPI / Pydantic，没有 async DB 栈。
- V1-D 的首要目标是持久化与日志，不是高并发 DB I/O。
- 同步 ORM 改造面更小，更适合从 `MemoryStore` 平滑过渡。

本轮不采用：

```text
SQLAlchemy async ORM + asyncpg
```

暂不采用原因：

- 会牵动 API dependency、service、repository、workflow 签名。
- 需要更大范围的 async transaction 管理。
- 当前没有独立 worker 或高并发要求。

### 7.2 PostgreSQL 本地开发方式

本轮确认：

- 新增 `DATABASE_URL`。
- 新增 `REPOSITORY_BACKEND`。
- `.env.example` 写入示例。
- PostgreSQL 作为目标 runtime。
- SQLite 只作为自动测试兼容路径，不作为业务验收替代。

配置建议：

```text
REPOSITORY_BACKEND=memory | database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/aesthetic_trajectory
TEST_DATABASE_URL=sqlite+pysqlite:///:memory:
```

验收原则：

- 自动测试可以使用 SQLite 降低本地依赖。
- V1-D 人工验收必须使用 PostgreSQL runtime 确认“服务重启后数据不丢失”。

### 7.3 Alembic 文件位置

本轮采用：

```text
backend/alembic.ini
backend/alembic/
backend/alembic/versions/
```

原因：

- Alembic 命令在 `backend` 目录运行更直接。
- 与 `backend/pyproject.toml` 和 `backend/app` 对齐。
- migration 不放入 `app/db`，避免 runtime db session 与 migration 管理混在一起。

命令约定：

```text
python -m alembic revision --autogenerate -m "initial v1 persistence schema"
python -m alembic upgrade head
```

### 7.4 初始 Migration 范围

初始 migration 包含：

- `users`
- `aesthetic_inputs`
- `input_features`
- `embedding_records`
- `analysis_jobs`
- `aesthetic_reports`
- `possible_interpretations`
- `insights`
- `insight_feedback`
- `analysis_logs`

采用原因：

- 与 `16-V1开发收口清单.md` 的 V1 表范围一致。
- `embedding_records` 虽然 ChromaDB runtime 暂缓，但 metadata 已在 V1-B workflow 中产生，需要持久化。
- 不把 ChromaDB vector 本体写入 PostgreSQL。

本轮不包含：

- `user_aesthetic_profiles`
- 历史报告索引表。
- report comparison 表。
- prompt version dashboard 表。
- 通用 audit_log 表。

### 7.5 DB Model 与 API Schema 分离

本轮采用：

```text
backend/app/models/          # SQLAlchemy DB model
backend/app/schemas/         # Pydantic API / workflow schema
```

规则：

- DB model 表达持久化结构。
- Pydantic schema 保持现有 API contract。
- repository 负责 DB model 与 Pydantic schema 的转换。
- 不让 SQLAlchemy model 直接作为 API response。
- 不为兼容数据库而改动前端 response shape。

### 7.6 JSON / JSONB 字段范围

PostgreSQL runtime 使用 JSONB：

- `input_features.feature_json`
- `aesthetic_reports.low_level_features_json`
- `aesthetic_reports.similarity_groups_json`
- `aesthetic_reports.interpretations_json`
- `aesthetic_reports.report_json`
- `possible_interpretations.evidence_json`
- `possible_interpretations.alternative_names_json`
- `insights.evidence_json`

SQLite 测试使用 SQLAlchemy JSON 兼容字段。

规则：

- JSON 字段保存结构化快照。
- 不保存 LLM raw output。
- 不保存图片二进制。
- 不保存密钥、token 或敏感配置。

### 7.7 Repository 切换策略

本轮采用配置切换：

```text
REPOSITORY_BACKEND=memory
REPOSITORY_BACKEND=database
```

默认值：

```text
memory
```

原因：

- 保持当前测试和 mock workflow 可运行。
- 可以逐步接入 database repository。
- 允许本地无 PostgreSQL 时继续跑基础自动测试。

实现原则：

- `memory` repository 保留现有行为。
- `database` repository 使用 SQLAlchemy session。
- service 层不直接依赖 `MemoryStore`。
- API dependency 根据 settings 创建对应 service / repository。

### 7.8 Workflow Transaction Boundary

V1-D 暂不把完整分析 workflow 包进单个大事务。

采用方式：

- 输入创建：单独事务。
- job 创建：单独事务。
- workflow 每个关键 step 完成后提交相关结果和 `analysis_logs`。
- report 保存和 job completed 更新应在同一 service 边界中完成。
- feedback 保存：单独事务。

原因：

- AI workflow 可能逐步变成长耗时流程。
- 单个大事务不适合覆盖 feature extraction / embedding / report generation。
- 分 step 提交更利于失败恢复和排错。

失败规则：

- step 开始时写 `running` 或记录 `started_at`。
- step 成功时写 `success`、`finished_at`、`latency_ms`。
- step 失败时写 `failed`、`error_type`、`error_message`。
- workflow 失败时更新 `analysis_jobs.status=failed` 和 `error_message`。

### 7.9 Analysis Logs 字段

本轮 `analysis_logs` 字段确认：

```text
id
job_id
step_id
status
model_name
prompt_version
latency_ms
error_type
error_message
started_at
finished_at
created_at
```

字段规则：

- `step_id` 使用稳定枚举式字符串。
- `status` 使用 `running | success | failed | skipped`。
- `model_name` 可为空。
- `prompt_version` 可为空。
- `latency_ms` 可为空，但 success / failed 时优先写入。
- `error_message` 只保存可排错摘要，不保存敏感上下文。

V1-D 建议 step ids：

```text
extract_features
generate_embeddings
write_vectors
cluster_inputs
generate_report
save_report
save_feedback
```

### 7.10 测试数据库策略

自动测试：

- repository 单元测试使用 SQLite in-memory。
- workflow / API 测试继续可在 memory backend 下运行。
- 新增 database repository 测试覆盖 save / get / get_many。
- Alembic migration 至少保证可导入和生成 metadata。

人工验收：

- 使用 PostgreSQL runtime。
- 执行 migration。
- 创建输入并生成报告。
- 重启服务。
- 查询 job / report / feedback 仍存在。
- 查询 `analysis_logs` 能看到 step / status / latency / error 字段。

### 7.11 API Response 策略

本轮不修改现有 API 路径和 response shape。

保持：

- input API 返回 `AestheticInputResponse`。
- analysis job API 返回 `AnalysisJobResponse`。
- report API 返回 `ReportResponse`。
- feedback API 返回 `InsightFeedbackResponse`。

允许内部变化：

- repository 从 memory 改为 database。
- response 从 DB model 转换得到。
- report 内部 JSON snapshot 可用于恢复 response。

### 7.12 最终实现顺序

1. 新增依赖：SQLAlchemy、psycopg、Alembic。
2. 新增 settings：`DATABASE_URL`、`TEST_DATABASE_URL`、`REPOSITORY_BACKEND`。
3. 新增 `backend/app/db/`：engine、session、base。
4. 新增 SQLAlchemy models。
5. 新增 Alembic 配置和初始 migration。
6. 新增 database repositories。
7. 调整 service dependency，使 memory / database 可切换。
8. 为 workflow 加入 `analysis_logs` 写入。
9. 补充 repository / workflow / API 测试。
10. 更新 `.env.example`。
11. 运行 `python -m pytest` 和 `npm run build`。
12. PostgreSQL runtime 人工验收。

## 8. 实现范围

### 8.1 数据库基础设施

需要新增：

- SQLAlchemy engine。
- Session factory。
- session dependency。
- declarative base。
- settings。
- Alembic env。

最低要求：

- `REPOSITORY_BACKEND=memory` 时现有行为不变。
- `REPOSITORY_BACKEND=database` 时使用 `DATABASE_URL`。

### 8.2 PostgreSQL Models

需要新增 V1 必需表 model：

- `UserModel`
- `AestheticInputModel`
- `InputFeatureModel`
- `EmbeddingRecordModel`
- `AnalysisJobModel`
- `AestheticReportModel`
- `PossibleInterpretationModel`
- `InsightModel`
- `InsightFeedbackModel`
- `AnalysisLogModel`

最低要求：

- 主键使用现有 string id。
- 时间字段使用 timezone-aware datetime。
- status / type / rating 使用字符串字段，暂不强制 DB enum。
- JSONB 字段保存结构化快照。

### 8.3 Database Repositories

需要新增或改造：

- input repository。
- analysis job repository。
- report repository。
- feedback repository。
- feature repository。
- embedding record repository。
- interpretation / insight repository。
- analysis log repository。

最低要求：

- 能保存当前 workflow 已产生的数据。
- 能按 API 需要查询 input / job / report / feedback。
- 不改变 API route。

### 8.4 Workflow Persistence

需要让当前 workflow 结果进入 database repository：

- features。
- embedding records metadata。
- groups / interpretations / insights。
- report。
- job status。
- analysis logs。

最低要求：

- mock workflow 仍可运行。
- PostgreSQL runtime 下服务重启后 report 可查询。
- 失败时能查到 job error 和 step log。

### 8.5 Analysis Logs

需要新增 workflow step log 写入能力。

最低要求：

- 每个主要 step 至少写 success log。
- 失败 step 写 failed log。
- log 包含 step / status / latency / modelName / promptVersion / error。
- 不记录敏感信息。

## 9. 不允许 AI 自行决定的内容

本轮禁止自行扩大范围：

- 不新增历史报告 UI。
- 不新增长期用户画像。
- 不让 feedback 更新画像权重。
- 不接 ChromaDB runtime。
- 不新增任务队列。
- 不新增 OpenTelemetry runtime。
- 不新增完整登录系统。
- 不改变现有 API 路径。

## 10. 预期涉及文件

后端可能涉及：

```text
backend/app/core/config.py
backend/app/db/
backend/app/models/
backend/app/repositories/
backend/app/workflows/aesthetic_analysis_v1.py
backend/app/workflows/steps/
backend/alembic/
backend/alembic.ini
backend/.env.example
backend/pyproject.toml
backend/app/tests/
```

文档可能涉及：

```text
docs/07-数据结构与系统架构文档.md
docs/08-项目目录结构与代码分层规范.md
docs/09-AI Workflow 编排与任务执行文档.md
docs/12-开发任务拆分与里程碑计划.md
docs/15-迭代执行记录.md
docs/archive/v1/V1-遗留问题.md
docs/archive/v1/V1-验收核对表.md
```

## 11. 验收标准

本轮完成需要满足：

- `python -m pytest` 通过。
- 前端 `npm run build` 仍通过。
- 服务重启后数据不丢失。
- 输入可查询。
- 报告可查询。
- 反馈可查询。
- analysis job 状态可查询。
- `analysis_logs` 能记录 step / status / modelName / promptVersion / latency / error。
- 保持当前 API 路径不变。
- mock workflow 仍可运行。

自动验证记录：

```text
2026-06-16：
- 已完成代码实现：SQLAlchemy DB model、Alembic 初始 migration、database repositories、memory/database backend 切换配置、workflow analysis_logs。
- 已新增 V1-D SQLite database repository 测试。
- 已验证 Alembic migration 可在 SQLite 测试库执行。
- `python -m pip install -e .`：通过。
- `python -m pytest`：14 passed，3 warnings。
- `npm run build`：通过。
- linter：未发现错误。

说明：
3 条 Pydantic UnsupportedFieldAttributeWarning 为既有 alias warning，未在 V1-D 中新增。
```

待人工验收：

```text
PostgreSQL runtime 路径：配置 REPOSITORY_BACKEND=database 和 DATABASE_URL → 执行 alembic upgrade head → 启动后端 → 上传不少于 3 条文字输入 → 生成报告 → 提交 feedback → 重启服务 → 查询 job / report / feedback 仍存在 → 检查 analysis_logs 中有 step / status / latency / error 字段。
```

人工验收记录：

```text
2026-06-16：
手动路径：使用 PostgreSQL runtime，配置 REPOSITORY_BACKEND=database 和 DATABASE_URL → 执行 alembic migration → 启动后端和前端 → 上传不少于 3 条文字输入 → 生成报告 → 提交 feedback → 检查 PostgreSQL 表数据。
结果：通过。
范围：PostgreSQL 连接、Alembic migration、database repository、aesthetic_inputs、analysis_jobs、aesthetic_reports、insight_feedback、analysis_logs。
限制：ChromaDB runtime、真实文件存储、历史报告 UI、用户画像更新仍不属于 V1-D。
```

## 12. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如 schema 或架构文档变化，更新 `07` / `08` / `09` / `16`。

## 13. 下一轮入口

如果本轮通过，下一轮进入：

```text
V1-E：稳定版验收
```

如果本轮未通过，继续收口：

```text
PostgreSQL runtime
repository
analysis_logs
migration
workflow persistence
```
