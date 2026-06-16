# V1-E：稳定版验收

当前状态：

```text
accepted / archived
```

创建日期：

```text
2026-06-16
```

## 1. 本轮目标

确认 V1 已形成可演示、可持久化、可反馈的稳定基线，并把 V1 最终验收结果沉淀到归档文档中。

本轮目标链路：

```text
前端上传
↓
后端输入保存
↓
分析任务执行
↓
feature / embedding metadata / similarity group / report / insight
↓
PostgreSQL 持久化
↓
前端报告展示
↓
insight feedback 保存
↓
analysis_logs 可查询
↓
V1 稳定版验收归档
```

## 2. 当前基线

当前已归档状态：

```text
V1-A accepted / archived
V1-B accepted / archived
V1-C accepted / archived
V1-D accepted / archived
```

已确认：

- V1-A 已完成 feature extraction 边界。
- V1-B 已完成 embedding metadata 与 similarity grouping 边界。
- V1-C 已完成 report / interpretation / insight / feedback 边界。
- V1-D 已完成 PostgreSQL persistence 和 `analysis_logs` 边界。
- 后端自动测试已通过。
- 前端 build 已通过。
- PostgreSQL runtime 人工验收已通过。

当前限制：

- 当前仍是 mock / heuristic workflow，不是真实 LLM / vision runtime。
- 图片真实文件存储仍未接入。
- ChromaDB runtime add/query 仍未接入。
- V2 历史报告和轻量画像未进入本轮。

## 3. 本轮解决什么问题

本轮解决：

```text
V1 是否可以作为当前稳定演示基线归档？
```

本轮不解决：

- 真实 LLM / vision runtime。
- 真实图片内容读取。
- ChromaDB runtime 检索。
- 历史报告列表。
- 长期用户画像。
- RAG。
- Agent。
- MCP。

## 4. 必须阅读的文档

只需要阅读以下文档：

1. `docs/12-开发任务拆分与里程碑计划.md`
2. `docs/13-验证与评估文档.md`
3. `docs/15-迭代执行记录.md`
4. `docs/16-V1开发收口清单.md`
5. `docs/archive/v1/V1-验收核对表.md`
6. `docs/archive/v1/V1-遗留问题.md`
7. `docs/iterations/v1-a-real-feature-extraction.md`
8. `docs/iterations/v1-b-embedding-similarity.md`
9. `docs/iterations/v1-c-report-feedback.md`
10. `docs/iterations/v1-d-persistence-logs.md`

不要一次性读取 `03-16` 全量文档。

## 5. 外部调研与方案选择

本节必须在执行 V1-E 最终验收前完成。

调研要求：

```text
本轮必须进行外部调研，并在本文档中记录。

调研重点不是新增功能，而是稳定版验收、发布前检查、冒烟测试、回归测试、数据库迁移验收和手动验收记录规范。
```

### 5.1 调研问题

本轮调研只围绕最终验收：

- 稳定版验收应覆盖哪些 release readiness 项目？
- 冒烟测试和回归测试应该如何划分？
- 数据库 migration 和持久化应如何验收？
- 手动验收记录应包含哪些信息？
- 哪些问题必须阻塞 V1 归档，哪些可以进入 V2/V3 遗留？

### 5.2 外部调研记录

当前状态：

```text
in_progress
```

#### 记录 1：pytest 测试执行与发现规则

来源名称：pytest documentation - How to invoke pytest

来源类型：官方文档

链接或出处：`https://docs.pytest.org/en/stable/how-to/usage.html`

调研问题：

- V1-E 自动测试应如何执行和记录？
- 是否应记录具体命令和测试发现规则？

核心做法：

- pytest 默认发现 `test_*.py` 或 `*_test.py`。
- 可以通过 `pytest` 或 `python -m pytest` 运行测试。
- 可以指定目录、文件、具体测试函数或 marker。
- `python -m pytest` 会把当前目录加入 `sys.path`，对本项目后端测试更稳定。

对 V1-E 的启发：

- V1-E 自动验收命令应继续使用 `python -m pytest`。
- 验收记录应明确测试总数、通过数、warning 数量和 warning 是否为已知问题。
- 如果最终验收失败，应记录失败测试名，而不是只写“测试失败”。

不能照搬：

- pytest 文档只说明测试执行机制，不定义产品验收 checklist。
- 不需要在 V1-E 引入 marker、并行测试或复杂测试筛选。

采用结论：

```text
采用 `python -m pytest` 作为 V1-E 后端自动验收命令，并记录通过数量、warning 和失败项。
```

#### 记录 2：FastAPI TestClient 测试

来源名称：FastAPI documentation - Testing / Using TestClient

来源类型：官方文档

链接或出处：`https://fastapi.tiangolo.com/tutorial/testing/#using-testclient`

调研问题：

- V1-E 是否需要保留 API flow 集成测试？
- FastAPI API 路径如何做自动验收？

核心做法：

- FastAPI 推荐使用 `TestClient` 测试应用。
- 测试函数使用标准 pytest 形式。
- 可以像 HTTP 客户端一样发送 GET / POST 请求。
- 使用普通 assert 检查状态码和 JSON response。
- 可覆盖成功路径和错误路径。

对 V1-E 的启发：

- 当前 `test_api_flow.py` 属于 V1-E 的核心回归测试，应保留并复跑。
- V1-E 自动验收应覆盖 `/api/inputs`、`/api/analysis-jobs`、`/api/reports/{id}`、`/api/insights/{id}/feedback`。
- V1-E 如果发现 API response shape 变化，应阻塞归档。

不能照搬：

- FastAPI 示例使用 toy app，不涉及数据库持久化和前端手动验收。
- V1-E 还需要 PostgreSQL runtime 和浏览器路径人工确认。

采用结论：

```text
采用现有 FastAPI TestClient API flow 作为 V1-E 自动验收的一部分；数据库持久化和浏览器路径仍需人工验收补充。
```

#### 记录 3：Alembic migration 执行与版本检查

来源名称：Alembic 官方文档：Tutorial / Commands / Autogenerate Check

来源类型：官方文档 / 数据库 migration 工具文档

链接或出处：`https://alembic.sqlalchemy.org/en/latest/tutorial.html`

调研问题：

- 如何确认 migration 已执行？
- 如何确认数据库 revision 已到最新 head？
- 如何发现 SQLAlchemy model 与数据库 schema 之间还有未生成的 migration？

核心做法：

- 使用 `alembic upgrade head` 将数据库迁移到最新 revision。
- 使用 `alembic current` 查看当前数据库 revision。
- 使用 `alembic heads` 查看代码侧 migration 脚本的最新 head。
- 使用 `alembic check` 检测是否还有未生成的 upgrade operations。
- 在自动化或 CI 中可把 migration check 作为防止 schema drift 的检查项。

对 V1-E 的启发：

- V1-E 的 migration 验收不能只看服务是否启动，必须记录 `alembic upgrade head` 已执行成功。
- PostgreSQL 持久化基线应记录 `alembic current` 输出，确认当前数据库 revision 已到 head。
- V1-E 应增加 `alembic check`，确认当前 model 与 migration 之间没有遗漏变更。
- 对 `analysis_logs` 表，不能只依赖 ORM 可访问；应确认 migration 后表真实存在、字段存在、可写入、可查询。
- V1-E 归档应记录 migration 命令、输出摘要、执行时间和数据库环境。

不能照搬：

- Alembic 文档主要说明 migration 工具机制，不提供完整产品验收规范。
- `alembic check` 只能发现 autogenerate 能识别的 schema 差异，不能替代业务级数据读写验证。
- V1-E 当前是稳定基线验收，不需要引入复杂多分支 migration 管理。

采用结论：

```text
采用 `alembic upgrade head` + `alembic current` + `alembic heads` + `alembic check` 作为 migration 自动验收基线；不把服务能启动等同于 migration 验收通过。
```

#### 记录 4：PostgreSQL information_schema 表结构检查

来源名称：PostgreSQL 官方文档：Information Schema

来源类型：官方文档 / 数据库 schema 检查资料

链接或出处：`https://www.postgresql.org/docs/current/information-schema.html`

调研问题：

- 如何确认 migration 后 PostgreSQL 表真实存在？
- 如何确认 schema 正确，而不是仅依赖 ORM 代码？
- 如何给 V1-E 留下可审计的数据库验收记录？

核心做法：

- 使用 `information_schema.tables` 检查目标表是否存在。
- 使用 `information_schema.columns` 检查关键字段是否存在、类型是否符合预期。
- 使用实际 SQL 查询检查表是否可读。
- 使用一次业务路径写入检查表是否可写。
- 使用 PostgreSQL 直接查询结果作为验收记录，而不是只看接口返回。

对 V1-E 的启发：

- 对 `analysis_logs` 必须检查：表存在、主键存在、分析记录字段存在、时间字段存在、状态字段存在。
- 对 embedding metadata、report、insight、feedback 相关持久化表，应至少检查核心表和核心字段。
- 对 FastAPI 接口，应通过 pytest 或手动流程触发一次完整分析，再到 PostgreSQL 查询是否落库。
- V1-E 应证明数据不是只存在内存里，而是 PostgreSQL 可查询、可复现。
- iteration 文档应附上数据库检查 SQL 和实际返回摘要。

不能照搬：

- `information_schema` 适合检查标准表、列、约束信息，但不一定覆盖所有 PostgreSQL 专有能力。
- 当前 V1-E 不需要做完整 DBA 级审计，例如索引性能分析、权限矩阵、备份恢复演练。
- 不需要为每个非核心字段都写复杂校验，重点放在演示链路依赖的核心表和字段。

采用结论：

```text
采用 PostgreSQL information_schema + 实际 SELECT 查询作为 schema 与数据可查询验收依据；不只依赖 SQLAlchemy model 或接口成功返回。
```

#### 记录 5：Google SRE launch checklist / release readiness

来源名称：Google SRE Book：Reliable Product Launches

来源类型：发布工程资料 / SRE 实践资料

链接或出处：`https://sre.google/sre-book/reliable-product-launches/`

调研问题：

- V1-E 发布 / 归档前 checklist 应包括哪些项？
- 如何避免 checklist 过度复杂，反而不适合 V1-E？
- 对一个可演示系统，release readiness 应该检查什么？

核心做法：

- 使用 checklist 确保发布前检查一致、完整。
- checklist 应围绕真实风险，而不是无限罗列。
- 对存储持久化数据的系统，应检查数据保存、查询、备份或恢复策略。
- 对可被用户使用的服务，应考虑异常输入、滥用风险或保护机制。
- checklist 应给出 action item，而不是只问抽象问题。

对 V1-E 的启发：

- V1-E 不是真正大规模生产发布，但应该有“稳定基线归档 checklist”。
- checklist 应覆盖：测试是否通过、migration 是否执行、PostgreSQL 数据是否可查、核心 API 是否可用、前端演示路径是否走通、反馈是否可保存。
- 对 `analysis_logs`，应明确它是 V1-E 的验收证据表。
- 对 FastAPI，应检查服务启动、核心接口、错误返回、日志记录。
- 对 React 前端，应检查最小演示路径，而不是追求完整 UI 测试自动化。

不能照搬：

- Google SRE 的 checklist 面向生产级服务，包含大规模运维、SLO、容量、滥用防护、跨团队协作。
- 当前 V1-E 是个人项目稳定基线验收，不需要完整 SRE PRR，也不需要复杂监控体系。
- 不需要引入正式发布审批流程，但需要有归档记录和阻塞项判断。

采用结论：

```text
采用轻量 release readiness checklist：测试、migration、数据库、核心链路、前端手动验收、日志与遗留问题归档；不采用生产级 SRE 全量发布流程。
```

#### 记录 6：ISTQB smoke test 与 regression testing 定义

来源名称：ISTQB Glossary：Smoke Test / Regression Testing

来源类型：测试方法说明 / 行业术语标准

链接或出处：

- `https://glossary.istqb.org/en_US/term/smoke-test`
- `https://glossary.istqb.org/en_US/term/regression-testing`

调研问题：

- 冒烟测试和回归测试分别是什么？
- V1-E 应如何设计 smoke test 和 regression test？
- V1-E 回归测试应覆盖哪些历史能力？

核心做法：

- 冒烟测试覆盖组件或系统主要功能，用于判断系统是否基本可测。
- 冒烟测试应短、稳定、可重复，失败通常意味着当前版本不能继续验收。
- 回归测试关注变更是否破坏已有能力。
- 回归测试不只测新增功能，也要测未改动但受影响的旧功能。
- 回归测试范围应根据当前 iteration 的改动风险选择。

对 V1-E 的启发：

- V1-E smoke test 应覆盖“系统是否能演示”：后端启动、数据库连接、核心 API 返回、前端页面打开、一次分析流程完成。
- V1-E regression test 应回归 V1-A 到 V1-D 的核心能力。
- V1-A 回归：特征抽取边界仍稳定。
- V1-B 回归：embedding metadata 与 similarity grouping 仍能生成。
- V1-C 回归：report、insight、feedback 仍能正常生成和保存。
- V1-D 回归：PostgreSQL persistence 与 `analysis_logs` 仍能写入、查询、关联到一次分析。

不能照搬：

- 不应把 smoke test 扩展成所有 pytest、所有 UI 路径、所有异常输入测试。
- 不需要为 V1-A 到 V1-D 每个历史细节都做完整回归。
- 不需要引入大型测试管理平台。
- 前端当前更适合手动验收记录，不强行覆盖所有 UI 细节自动化。

采用结论：

```text
采用 smoke test 作为 V1-E 第一层验收；采用面向 V1-A 至 V1-D 核心能力的轻量 regression test。自动化优先覆盖 API、service、database，前端以手动验收补充。
```

#### 记录 7：手动测试执行与结果记录

来源名称：Microsoft Learn：Run Manual Tests with Azure Test Plans

来源类型：官方文档 / 手动测试记录规范

链接或出处：`https://learn.microsoft.com/en-us/azure/devops/test/run-manual-tests?view=azure-devops`

调研问题：

- 手动验收记录应该包含什么？
- 前端手动验收如何做到可追踪？
- 失败结果和 bug / 遗留问题如何关联？

核心做法：

- 每个测试步骤应有预期结果。
- 每个验证步骤应标记 passed / failed。
- 失败时记录失败原因、评论、截图或诊断信息。
- 失败项应创建或关联 bug。
- 测试结束后保存测试状态，便于回看历史结果。

对 V1-E 的启发：

- React 前端手动验收记录应包含：页面路径、操作步骤、输入样例、预期结果、实际结果、是否通过。
- 对 report / insight / feedback 页面，应记录“能否展示、能否提交、提交后是否写入 PostgreSQL”。
- 对 `analysis_logs`，手动验收不能只写“前端成功”，还要记录对应查询结果。
- 对限制项应单独写：当前未做鉴权、未做大规模并发、未做 UI 自动化、未做生产监控。
- 对失败项应明确归类为 blocking 或 non-blocking，并写入 iteration 归档。

不能照搬：

- Azure Test Plans 是完整测试管理平台，当前项目不需要引入。
- 不需要建立复杂测试套件管理界面。
- 当前只需要 Markdown 文档中的手动验收记录即可。

采用结论：

```text
采用 Markdown 手动验收记录：路径、步骤、预期结果、实际结果、状态、证据、遗留问题；不引入 Azure Test Plans 等测试管理平台。
```

#### 记录 8：Severity / priority / blocking 分类

来源名称：ISTQB Glossary：Severity；Atlassian Jira：Priority / Severity / Blocked

来源类型：测试术语标准 / 缺陷管理实践资料

链接或出处：

- `https://glossary.istqb.org/en_US/term/severity`
- `https://www.atlassian.com/incident-management/kpis/severity-levels`

调研问题：

- 阻塞问题和非阻塞遗留问题如何分类？
- blocking、severity、priority 有什么区别？
- V1-E 归档时哪些问题必须修，哪些可以留到 V2？

核心做法：

- severity 描述影响程度。
- priority 描述修复顺序。
- blocked 表示当前工作无法继续推进。
- blocker / critical / major / minor / trivial 可作为问题分级词汇。
- 问题分类应结合用户影响、数据风险、核心路径、是否有绕过方案、是否影响验收。

对 V1-E 的启发：

- V1-E 的 blocking issue 应定义为：影响可演示、可持久化、可反馈稳定基线成立的问题。
- 如果 FastAPI 核心分析接口失败、PostgreSQL migration 未执行、`analysis_logs` 无法写入、反馈无法保存，应判定为阻塞。
- 如果 UI 文案不完美、样式不统一、非核心边缘输入未处理，可作为非阻塞遗留。
- 如果问题影响 V1-A 到 V1-D 的已完成能力，应提高优先级。
- 所有遗留问题必须写明：影响范围、是否有 workaround、计划处理版本。

不能照搬：

- Jira 的 blocker / critical / major 等默认优先级不能直接等同于本项目的验收结论。
- V1-E 不需要复杂 issue tracking workflow。
- 不应因为一个问题名称叫 critical 就自动阻止归档，必须结合 V1-E 目标判断。

采用结论：

```text
采用“是否破坏 V1-E 稳定基线”作为 blocking 判断标准；采用 severity 描述影响，priority 决定修复顺序，不机械照搬 Jira 默认等级。
```

### 5.3 调研结论与可借鉴模式

本轮可采用：

- `python -m pytest` 作为后端自动验收命令。
- FastAPI `TestClient` API flow 作为核心回归测试。
- Alembic migration 以 `upgrade head`、`current`、`heads`、`check` 组合验证。
- PostgreSQL `information_schema` 与实际 SELECT 查询作为数据库验收依据。
- 轻量 release readiness checklist。
- smoke test 作为最小可演示主链路检查。
- regression test 覆盖 V1-A 到 V1-D 的核心能力。
- Markdown 手动验收记录。
- blocking / non-blocking 遗留问题分类。

本轮不采用：

- 生产级 SRE 全量发布流程。
- 大型测试管理平台。
- 完整 UI 自动化测试框架。
- 复杂 issue tracking workflow。
- 备份恢复演练、容量评估、并发压测等生产化检查。

### 5.4 本轮采用方案

外部调研后采用：

```text
自动验收：python -m pytest + npm run build + Alembic migration/status/check
手动验收：React 主路径上传 3-10 个样本 → 分析 → 报告 → feedback
数据库验收：PostgreSQL information_schema + 核心表 SELECT
日志验收：analysis_logs step / status / latency / error 可查询
归档验收：V1 验收核对表、遗留问题、归档说明同步
问题分类：以是否破坏 V1-E 稳定基线作为 blocking 判断标准
```

设计确认结果：

- V1-E 最终验收 checklist：已确认。
- 自动测试范围：已确认。
- 手动测试路径：已确认。
- PostgreSQL 数据检查范围：已确认。
- `analysis_logs` 检查范围：已确认。
- V1 归档结论格式：已确认。
- V1 遗留问题分类：已确认。
- Git 策略：本轮只提交普通 commit，不创建 tag；如后续需要 release tag 再单独执行。

## 6. 系统边界

本轮包含的能力：

- V1 最终验收范围确认。
- 自动测试复跑。
- 前端 build 复跑。
- PostgreSQL runtime 路径复验。
- 前端完整路径复验。
- V1 归档文档更新。
- V1 遗留问题更新。

本轮暂缓的能力：

- 新增后端功能。
- 新增前端功能。
- 新增数据库表。
- 接真实模型。
- 接 ChromaDB runtime。

本轮明确不做：

- V2 历史报告。
- V2 轻量画像。
- V3 personalized retrieval。
- V4 Agent / MCP。

## 7. 设计确认

当前状态：

```text
confirmed
```

本节把外部调研结论落成 V1-E 可执行验收方案。完成本节后，V1-E 可以进入最终验收执行。

### 7.1 V1-E 验收分层

V1-E 分为四层验收：

```text
1. 自动验收
2. 数据库 / migration 验收
3. 浏览器手动验收
4. 文档归档验收
```

通过标准：

```text
四层验收均无 blocking issue，V1 才能归档为稳定版基线。
```

### 7.2 自动验收 Checklist

必须执行：

```text
[ ] python -m pytest
[ ] npm run build
[ ] python -m alembic upgrade head
[ ] python -m alembic current
[ ] python -m alembic heads
[ ] python -m alembic check
```

记录要求：

- 记录命令。
- 记录结果。
- 记录 passed / failed 数量。
- 记录 warning 数量。
- 对既有 warning 标注是否为已知可接受风险。

通过标准：

- pytest 全量通过。
- 前端 build 通过。
- Alembic 数据库 revision 到 head。
- Alembic check 无 pending upgrade operations。

### 7.3 手动验收 Checklist

浏览器路径：

```text
[ ] 启动 PostgreSQL runtime 后端
[ ] 启动 React 前端
[ ] 打开前端页面
[ ] 输入或上传 3-10 个样本
[ ] 触发分析任务
[ ] 分析任务完成
[ ] 报告页展示 summary
[ ] 报告页展示 lowLevelFeatures
[ ] 报告页展示 similarityGroups
[ ] 报告页展示 possibleInterpretations
[ ] 报告页展示 insights
[ ] insight 有 evidenceRefs
[ ] insight 有 uncertainty
[ ] 提交 insight feedback
[ ] 页面显示反馈保存成功
```

记录要求：

- 记录输入类型和数量。
- 记录操作路径。
- 记录预期结果。
- 记录实际结果。
- 记录是否通过。
- 如失败，记录截图或错误信息。

### 7.4 PostgreSQL 表检查 Checklist

必须检查：

```text
[ ] alembic_version
[ ] users
[ ] aesthetic_inputs
[ ] input_features
[ ] embedding_records
[ ] analysis_jobs
[ ] aesthetic_reports
[ ] possible_interpretations
[ ] insights
[ ] insight_feedback
[ ] analysis_logs
```

建议 SQL：

```sql
SELECT version_num FROM alembic_version;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'analysis_logs'
ORDER BY ordinal_position;

SELECT *
FROM analysis_logs
ORDER BY created_at DESC
LIMIT 5;
```

通过标准：

- 核心表存在。
- migration 版本为 head。
- 完整分析路径后核心表有数据。
- 重启后 job / report / feedback 仍可查询。

### 7.5 Analysis Logs 检查 Checklist

必须检查：

```text
[ ] 本次分析有 analysis_logs 记录
[ ] 记录包含 job_id
[ ] 记录包含 step_id
[ ] 记录包含 status
[ ] 记录包含 latency_ms
[ ] 记录包含 started_at / finished_at / created_at
[ ] 成功步骤 status 为 success
[ ] 失败时能记录 error_type / error_message
```

V1-E 期望看到的 step：

```text
extract_features
generate_embeddings
write_vectors
cluster_inputs
generate_report
save_report
```

### 7.6 Blocking / Non-Blocking 分类

blocking issue：

```text
FastAPI 服务无法启动
PostgreSQL 无法连接
alembic upgrade head 失败
alembic current 未到 head
alembic check 发现影响核心表的 pending migration
核心分析 API 无法完成
report / insight 无法生成
feedback 无法保存
analysis_logs 不生成记录
核心数据只存在内存，PostgreSQL 不可查询
前端主演示路径无法走通
pytest 核心用例失败
出现数据丢失、错误覆盖、不可恢复异常
```

non-blocking issue：

```text
UI 样式不统一，但不影响主流程
文案、提示语、布局存在优化空间
非核心异常输入未完全覆盖
暂未实现 UI 自动化测试
暂未实现鉴权
暂未实现生产级日志监控
暂未实现并发压测
暂未实现备份恢复演练
个别 insight 解释质量可优化，但 report 生成链路稳定
有明确 workaround，不影响 V1-E 可演示、可持久化、可反馈基线
```

判断原则：

```text
是否破坏“可演示、可持久化、可反馈”的稳定基线。
```

### 7.7 文档归档 Checklist

V1-E 通过后必须更新：

```text
[ ] docs/15-迭代执行记录.md
[ ] docs/archive/v1/V1-验收核对表.md
[ ] docs/archive/v1/V1-遗留问题.md
[ ] docs/archive/v1/V1-归档说明.md
[ ] docs/12-开发任务拆分与里程碑计划.md
[ ] docs/README.md
```

归档结论格式：

```text
V1 stable baseline accepted / archived

已确认：
- 自动测试通过
- 前端 build 通过
- PostgreSQL migration 和数据查询通过
- 前端完整路径通过
- feedback 保存通过
- analysis_logs 可查询

仍不包含：
- 真实 LLM / vision runtime
- 真实图片文件存储
- ChromaDB runtime add/query
- V2 历史报告
- V2 轻量画像
```

### 7.8 最终执行顺序

```text
1. 确认当前分支和工作区状态。
2. 执行 python -m pytest。
3. 执行 npm run build。
4. 执行 python -m alembic upgrade head。
5. 执行 python -m alembic current。
6. 执行 python -m alembic heads。
7. 执行 python -m alembic check。
8. 启动 PostgreSQL runtime 后端和前端。
9. 手动跑通 3-10 个样本的完整路径。
10. 在 PostgreSQL 中检查核心表和 analysis_logs。
11. 按 blocking / non-blocking 规则分类问题。
12. 更新归档文档。
13. 如果无 blocking issue，V1-E 标记为 accepted / archived。
```

## 8. 实现范围

V1-E 不新增产品功能，只执行验收和文档归档。

### 8.1 自动验收

执行并记录：

- 后端测试。
- 前端构建。
- Alembic migration / current / heads / check。

### 8.2 手动验收

执行并记录：

- 前端完整路径。
- PostgreSQL 数据检查。
- analysis_logs 检查。

### 8.3 文档归档

更新并记录：

- V1-E 任务单。
- 总执行记录。
- V1 验收核对表。
- V1 遗留问题。
- V1 归档说明。

## 9. 不允许 AI 自行决定的内容

本轮禁止自行扩大范围：

- 不新增产品功能。
- 不新增数据库 schema。
- 不改变 API 路径。
- 不改变报告结构。
- 不把 V2/V3/V4 能力提前塞进 V1-E。

## 10. 预期涉及文件

文档可能涉及：

```text
docs/12-开发任务拆分与里程碑计划.md
docs/13-验证与评估文档.md
docs/15-迭代执行记录.md
docs/16-V1开发收口清单.md
docs/archive/v1/V1-验收核对表.md
docs/archive/v1/V1-遗留问题.md
docs/archive/v1/V1-归档说明.md
docs/iterations/v1-e-stable-acceptance.md
```

代码一般不涉及，除非验收发现阻塞 bug。

## 11. 验收标准

本轮完成需要满足：

- `python -m pytest` 通过。
- `npm run build` 通过。
- PostgreSQL runtime migration 已是 head。
- 前端 3-10 个样本上传路径通过。
- report 可生成。
- insight feedback 可保存。
- PostgreSQL 表中可查询 input / job / report / feedback / analysis_logs。
- V1 遗留问题已分类。
- V1 验收核对表已更新。
- V1 归档结论已更新。

验收执行记录：

```text
2026-06-16：
自动验收：
- `python -m pytest`：14 passed，3 warnings。
- `npm run build`：通过。
- `python -m alembic upgrade head`：通过。
- `python -m alembic current`：20260616_0001 (head)。
- `python -m alembic heads`：20260616_0001 (head)。
- `python -m alembic check`：No new upgrade operations detected。

PostgreSQL 验收：
- `alembic_version`：20260616_0001。
- 核心表存在：aesthetic_inputs、aesthetic_reports、analysis_jobs、analysis_logs、embedding_records、input_features、insight_feedback、insights、possible_interpretations、users。
- 核心表已有数据：aesthetic_inputs=14、analysis_jobs=3、aesthetic_reports=3、insight_feedback=3、analysis_logs=18。
- `analysis_logs` 字段包含：id、job_id、step_id、status、model_name、prompt_version、latency_ms、error_type、error_message、started_at、finished_at、created_at。
- 最近日志包含 success：save_report、generate_report、cluster_inputs、write_vectors、generate_embeddings。

blocking 判断：
- 未发现 blocking issue。
- 既有 Pydantic alias warning 继续作为 non-blocking 遗留观察项记录。

结论：
V1-E 稳定版验收通过，可以归档为 V1 stable baseline。
```

## 12. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-验收核对表.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-归档说明.md`
- `docs/12-开发任务拆分与里程碑计划.md`

## 13. 下一轮入口

如果本轮通过，下一轮进入：

```text
V2：历史报告与轻量画像
```

如果本轮未通过，继续收口：

```text
V1 blocking bugs
V1 validation gaps
V1 archive docs
```
