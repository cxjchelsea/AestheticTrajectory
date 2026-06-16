# V2-A：历史报告列表与详情回看

当前状态：

```text
accepted / archived
```

创建日期：

```text
2026-06-16
```

## 1. 本轮目标

在 V1 stable baseline 的基础上，让用户可以查看自己过往生成的审美报告，并能从历史列表进入报告详情回看。

本轮目标链路：

```text
用户完成多次分析
↓
报告写入 PostgreSQL / MemoryStore
↓
用户打开历史报告页
↓
按时间倒序查看报告摘要
↓
点击一条历史报告
↓
复用现有报告详情页完整回看
```

## 2. 当前基线

当前已归档状态：

```text
V1 stable baseline accepted / archived
```

已确认：

- V1 可以保存输入、分析任务、报告、洞察、反馈和 `analysis_logs`。
- `aesthetic_reports` 已包含 `user_id`、`job_id`、`title`、`summary`、`report_json`、`created_at`。
- 后端已有 `GET /api/reports/{report_id}`。
- 前端已有 `ReportDetailPage`，可以展示完整 `ReportResponse`。

当前限制：

- 当前前端没有历史报告页。
- 当前后端没有按用户列出历史报告的 API。
- 当前仍使用匿名用户，不引入登录系统。
- 当前不做轻量画像、反馈权重、报告对比、RAG、Agent。

## 3. 本轮解决什么问题

本轮解决：

```text
用户能否回看自己过去生成过的报告？
```

本轮不解决：

- 轻量用户画像。
- 最近两次报告对比。
- 反馈权重更新。
- personalized retrieval。
- RAG。
- Agent。
- 登录系统或复杂权限。
- ChromaDB runtime 检索。

## 4. 必须阅读的文档

本轮只需要阅读：

1. `docs/02-版本迭代路线图.md`
2. `docs/03-MVP功能需求文档.md`
3. `docs/07-数据结构与系统架构文档.md`
4. `docs/11-模块拆分与接口测试文档.md`
5. `docs/12-开发任务拆分与里程碑计划.md`
6. `docs/15-迭代执行记录.md`
7. `docs/iterations/v1-e-stable-acceptance.md`

不要一次性扩大到 V3 / V4 文档范围。

## 5. 外部调研与方案选择

本节必须在实现 V2-A 前完成。

调研要求：

```text
本轮必须进行外部调研，并在本文档中记录。

调研重点是历史列表 UX、分页与排序 API、匿名用户历史隔离、报告摘要字段、空状态和手动验收记录。
```

### 5.1 调研问题

- 历史报告列表应该展示哪些最小信息？
- 历史列表 API 应如何处理分页、排序和默认限制？
- 匿名用户历史如何做最小隔离，避免看到其他用户报告？
- 空状态应该如何表达，才能引导用户创建第一份报告？
- 手动验收应如何记录历史列表和详情回看路径？

### 5.2 外部调研记录

当前状态：

```text
completed
```

#### 记录 1：历史列表与空状态 UX

来源名称：Nielsen Norman Group - Designing Empty States in Complex Applications

来源类型：UX 研究资料

链接或出处：`https://www.nngroup.com/articles/empty-state-interface-design/`

调研问题：

- 历史报告为空时应该怎么展示？
- 历史页是否应该只显示空白列表？

核心做法：

- 空状态不应该留白，否则用户会困惑并降低信心。
- 空状态应该说明当前没有什么内容、为什么没有、用户下一步可以做什么。
- 对内容型页面，空状态可以作为引导用户完成关键任务的入口。

对 V2-A 的启发：

- 历史报告页无数据时不能只显示“暂无数据”。
- 应明确写出“还没有历史报告”，并提供“开始一次审美分析”的入口。
- 空状态不应该暗示系统错误。

不能照搬：

- NN/G 面向复杂应用的空状态设计，本项目只需要轻量页面，不引入复杂 onboarding。

采用结论：

```text
V2-A 历史空状态采用明确说明 + 单一下一步操作：提示用户先完成一次分析。
```

#### 记录 2：列表 API 的排序与分页

来源名称：Microsoft REST API Guidelines - Collections / Sorting / Pagination

来源类型：API 设计规范

链接或出处：`https://github.com/Microsoft/api-guidelines/blob/master/Guidelines.md`

调研问题：

- 历史报告列表 API 是否需要分页？
- 列表排序如何保证稳定？

核心做法：

- 返回集合的 API 应考虑分页，避免未来数据增长后破坏兼容性。
- 分页和排序组合时，排序必须稳定。
- 排序、过滤、分页组合时，通常先过滤，再排序，再分页。
- 客户端驱动分页可以使用 `skip` / `top` 或等价参数。

对 V2-A 的启发：

- 即使当前历史报告数量很少，也应为列表接口保留 `limit` / `offset`。
- 默认按 `createdAt desc` 返回历史报告。
- 为了稳定排序，后端应在 `created_at desc` 后追加 `id desc` 作为 tie-breaker。
- V2-A 暂不开放复杂排序参数，避免 API 过早膨胀。

不能照搬：

- 不采用 OData 的 `$top`、`$skip`、`$orderby` 命名，保持本项目 API 简洁。
- 不引入 server-driven continuation token。

采用结论：

```text
V2-A 列表 API 采用 `limit` / `offset`，默认 `created_at desc, id desc`，不开放复杂排序。
```

#### 记录 3：对象级授权与用户历史隔离

来源名称：OWASP API Security Top 10 - API1:2023 Broken Object Level Authorization

来源类型：安全规范

链接或出处：`https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/`

调研问题：

- 历史报告列表如何避免看到其他用户报告？
- 报告详情回看是否需要对象级检查？

核心做法：

- 任何使用客户端传入 ID 访问数据库对象的 API，都应做对象级授权检查。
- 缺少对象级授权会导致未授权信息泄露。
- 应编写测试证明用户不能访问不属于自己的对象。

对 V2-A 的启发：

- 历史列表必须按 `user_id` 过滤。
- 历史列表测试必须覆盖“用户 A 看不到用户 B 的报告”。
- 现有 `GET /api/reports/{report_id}` 暂不改变响应结构，但 V2-A 需要记录后续应补充 user scope 的风险。
- 当前匿名用户体系还没有服务端 session，V2-A 以传入 `user_id` 作为最小可用边界，后续登录系统或 session 接入后应替换为服务端身份上下文。

不能照搬：

- 本项目当前没有 JWT、RBAC 或租户体系，不引入完整权限框架。
- 不在 V2-A 实现登录系统。

采用结论：

```text
V2-A 先在列表 API 上强制 `user_id` 过滤，并用测试覆盖用户隔离；详情接口的 user scope 作为后续安全增强记录，不改变 V1 API。
```

#### 记录 4：Material Design 空状态

来源名称：Material Design - Empty states

来源类型：设计规范

链接或出处：`https://m1.material.io/patterns/empty-states.html`

调研问题：

- 空历史页是否需要教育用户？
- 空状态应该展示什么语气？

核心做法：

- 空状态发生在列表或内容无法展示时，应避免用户困惑。
- 可以用简短 tagline 说明页面用途。
- 对新用户，可以提供 starter content 或教育性说明。

对 V2-A 的启发：

- 历史报告页空状态应说明：“完成一次分析后，这里会保存你的报告。”
- 可以提供“开始分析”按钮，而不是提供假历史数据。
- 语气应克制，不制造长期画像或成长结论。

不能照搬：

- 不引入插画系统或 starter content。
- 不展示示例报告作为真实历史。

采用结论：

```text
V2-A 空状态只做简短说明和开始分析入口，不生成示例历史。
```

#### 记录 5：手动验收记录

来源名称：Microsoft Learn - Record Actual Results for Manual Test Runs

来源类型：官方测试管理文档

链接或出处：`https://learn.microsoft.com/en-us/azure/devops/test/actual-result?view=azure-devops`

调研问题：

- V2-A 手动验收应记录什么？
- 历史列表与详情回看的验收证据如何保存？

核心做法：

- 手动测试应记录 expected result 和 actual result。
- 每个测试步骤应标记 pass / fail。
- actual result 是事实结果，可作为审计证据。
- 失败时应记录原因、评论或附件。

对 V2-A 的启发：

- 手动验收记录要包含：测试路径、输入数据、预期结果、实际结果、状态。
- 历史报告验收要记录：至少 2 次报告生成、列表倒序、点击详情、空状态。
- 若失败，要分类为 blocking 或 non-blocking。

不能照搬：

- 不引入 Azure Test Plans。
- 不建立复杂测试管理平台。

采用结论：

```text
V2-A 继续用 Markdown 记录手动验收，明确 expected / actual / pass-fail。
```

### 5.3 调研结论与采用方案

当前状态：

```text
completed
```

本轮采用：

- 历史报告列表只展示当前匿名用户的报告。
- 列表 API 支持 `limit` / `offset`，默认倒序。
- 排序使用 `created_at desc, id desc` 保证稳定。
- 每条历史 summary 返回最小字段：`reportId`、`jobId`、`title`、`summary`、`inputCount`、`createdAt`。
- 空状态提供“开始一次分析”的入口。
- 手动验收使用 Markdown 记录 expected / actual / pass-fail。

本轮不采用：

- 登录系统。
- JWT / RBAC / 多租户权限框架。
- 复杂排序过滤。
- server-driven continuation token。
- 示例历史报告。
- 画像、对比、推荐、RAG、Agent。

## 6. 系统边界

本轮包含：

- 历史报告 summary schema。
- 按匿名用户查询历史报告列表。
- 历史报告列表 API。
- 前端历史报告页。
- 从历史列表进入报告详情。
- 空状态。
- 后端自动测试和前端 build 验收。

本轮暂缓：

- 轻量画像。
- 报告对比。
- 反馈权重。
- 历史趋势图。
- 周报 / 月报。
- 登录系统。

本轮明确不做：

- 推荐系统。
- RAG。
- Agent。
- MCP。
- 知识图谱。
- 多用户复杂权限。

## 7. 初始验收标准

本轮完成需要满足：

- 用户可以打开历史报告列表。
- 列表只展示当前匿名用户的报告。
- 历史报告按创建时间倒序。
- 每条历史记录包含 `reportId`、`createdAt`、`title`、`summary`、`inputCount`、`jobId`。
- 点击历史记录可以进入报告详情页。
- 无历史报告时有明确空状态。
- 不引入登录系统。
- 不实现画像更新。
- 不实现报告对比。
- 后端测试通过。
- 前端构建通过。
- PostgreSQL runtime 手动验收有记录。

## 8. 预期涉及文件

后端可能涉及：

```text
backend/app/schemas/report.py
backend/app/repositories/report_repository.py
backend/app/repositories/database_repositories.py
backend/app/services/report_service.py
backend/app/api/routes/reports.py
backend/app/tests/
```

前端可能涉及：

```text
frontend/src/types/aesthetic.ts
frontend/src/services/reportApi.ts
frontend/src/app/App.tsx
frontend/src/pages/HistoryPage.tsx
frontend/src/pages/ReportDetailPage.tsx
frontend/src/styles/global.css
```

文档涉及：

```text
docs/12-开发任务拆分与里程碑计划.md
docs/15-迭代执行记录.md
docs/iterations/v2-a-report-history.md
docs/README.md
README.md
```

## 9. 不允许 AI 自行决定的内容

- 不新增登录系统。
- 不把匿名用户历史扩展成复杂权限系统。
- 不把历史列表做成画像或推荐。
- 不改变现有 `GET /api/reports/{report_id}` 的响应结构。
- 不改变 V1 report schema。
- 不引入新的前端路由库。
- 不提前实现 V2-B / V2-C。

## 10. 下一步

```text
V2-A 已通过验收；但 V2 缺少版本级 Memory / User Model 调研与架构拆分，下一步先进入 V2-0。
```

## 11. 设计确认

当前状态：

```text
confirmed
```

### 11.1 后端 Schema

新增：

```text
ReportSummary
- reportId: string
- jobId: string | null
- title: string
- summary: string
- inputCount: int
- createdAt: datetime

ReportHistoryResponse
- reports: list[ReportSummary]
- total: int
- limit: int
- offset: int
```

说明：

- `ReportSummary` 不返回完整 `report_json`，避免列表过重。
- `inputCount` 优先来自 `analysis_jobs.input_count`，没有 job 时回退为 `0`。
- 历史详情继续使用现有 `ReportResponse` 和 `GET /api/reports/{report_id}`。

### 11.2 后端 API

新增：

```text
GET /api/users/{user_id}/reports?limit=20&offset=0
```

响应：

```json
{
  "reports": [
    {
      "reportId": "report_001",
      "jobId": "job_001",
      "title": "审美分析报告",
      "summary": "低饱和、结构感和空旷空间反复出现。",
      "inputCount": 5,
      "createdAt": "2026-06-16T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

约束：

- `limit` 默认 20，范围 1-50。
- `offset` 默认 0，最小 0。
- 只查询 `user_id` 匹配的报告。
- 默认排序：`created_at desc, id desc`。

### 11.3 Repository / Service 契约

Memory repository：

```text
list_by_user(user_id: str, limit: int, offset: int) -> ReportHistoryResponse
```

Database repository：

```text
list_by_user(user_id: str, limit: int, offset: int) -> ReportHistoryResponse
```

Service：

```text
list_user_reports(user_id: str, limit: int = 20, offset: int = 0) -> ReportHistoryResponse
```

### 11.4 前端契约

新增：

```text
AppRoute: "history"
HistoryPage
getReportHistory(userId, limit?, offset?)
ReportSummary / ReportHistoryResponse types
```

页面行为：

- 首页提供“查看历史报告”入口。
- 报告详情页提供“查看历史报告”入口。
- 历史页加载当前匿名用户的报告。
- 空列表展示解释和“开始一次分析”按钮。
- 点击历史项调用现有 `getReport(reportId)`，然后进入既有 `ReportDetailPage`。

匿名用户：

- V2-A 暂时使用前端常量 `user_anonymous`，与后端 V1 默认用户保持一致。
- 后续登录或浏览器持久匿名 ID 不在本轮实现。

### 11.5 测试设计

后端测试：

- memory repository 按时间倒序返回。
- database repository 按用户过滤。
- 空历史返回空列表和 total=0。
- API flow 能创建报告后查询历史列表。

前端验收：

- `npm run build` 通过。
- 历史页有空状态。
- 历史页能展示至少 2 条报告。
- 点击历史报告能进入详情。

### 11.6 Blocking / Non-Blocking

blocking：

- 历史列表接口无法返回当前用户报告。
- 历史列表泄露其他用户报告。
- 点击历史记录无法打开详情。
- 现有报告详情 API 被破坏。
- 后端测试失败或前端 build 失败。

non-blocking：

- 暂无分页 UI。
- 暂无复杂过滤和搜索。
- 暂无登录系统。
- 暂无报告对比和画像。

## 12. 实现记录

2026-06-16 已完成：

后端：

- 新增 `ReportSummary` 和 `ReportHistoryResponse`。
- 新增 `GET /api/users/{user_id}/reports?limit=20&offset=0`。
- `ReportService` 新增 `list_user_reports`。
- memory repository 新增 `report_metadata` 和 `list_by_user`。
- database repository 新增按用户查询历史报告，排序为 `created_at desc, id desc`。
- 后端测试新增历史列表覆盖：API flow、database repository 用户隔离、倒序和 `inputCount`。

前端：

- `AppRoute` 新增 `history`。
- 新增 `HistoryPage`，支持加载、错误、空状态、历史报告列表和详情回看。
- `reportApi` 新增 `getReportHistory`。
- 首页新增“查看历史报告”入口。
- 报告页新增“历史报告”入口。
- 样式新增历史卡片和空状态。

未改变：

- 未改变 `GET /api/reports/{report_id}`。
- 未改变 V1 `ReportResponse`。
- 未新增数据库表或 migration。
- 未引入登录系统、画像、报告对比、RAG 或 Agent。

## 13. 验收记录

自动验收：

```text
2026-06-16：
命令：python -m pytest
结果：通过，15 passed，3 warnings。
范围：
- V1 API flow
- V2-A history API
- database repository list_by_user
- 用户隔离
- 倒序返回
- 既有 workflow / feature / embedding / report / feedback 测试
说明：
- 3 条 warning 为既有 Pydantic alias warning。

2026-06-16：
命令：npm run build
结果：通过。
范围：
- TypeScript build
- Vite production build
- V2-A HistoryPage / route / API type 编译
```

PostgreSQL runtime 验收：

```text
2026-06-16：
方式：REPOSITORY_BACKEND=database，使用 FastAPI TestClient 创建两次分析任务。
结果：通过。
证据：
- repository_backend=database
- created_report_ids=['report_1faaf2f9540d', 'report_4c1e2756be4f']
- history_total=7
- latest_history_report.reportId=report_4c1e2756be4f
- latest_history_report.inputCount=3
- `GET /api/reports/{report_id}` 可读取 latest_history_report 详情。
```

手动验收记录：

```text
路径：创建至少 2 次分析 → 打开历史列表 API → 检查倒序 summary → 点击最新报告详情 API。
预期结果：历史列表包含当前用户报告，最新报告在前，详情可回看。
实际结果：通过。
状态：pass。
```

## 14. 归档结论

```text
V2-A 历史报告列表与详情回看 accepted / archived。

已确认：
- 用户可以查询历史报告列表。
- 列表按当前匿名用户过滤。
- 列表按创建时间倒序。
- 每条历史记录包含 reportId / jobId / title / summary / inputCount / createdAt。
- 历史详情继续复用现有 ReportDetailPage。
- 无历史时有明确空状态。

仍不包含：
- 登录系统。
- 轻量画像。
- 反馈权重。
- 报告对比。
- RAG / Agent / MCP。
```

## 15. V2-0 后复核

2026-06-16 完成 V2-0 Memory / User Model 版本级调研与架构拆分后，复核 V2-A 结论：

```text
V2-A 保留为历史报告基础设施。
当前实现不生成画像、不写入 profile、不做反馈权重、不做报告对比。
后续 V2-B 可以复用 reportId / jobId / summary / inputCount / createdAt 作为 profile evidence 的上游入口。
```

当前不修改 V2-A 代码：

- 暂不扩展历史 summary 字段。
- 暂不改变 `GET /api/users/{user_id}/reports`。
- 暂不改变 `GET /api/reports/{report_id}`。
- 暂不改变前端固定匿名用户 ID。

这些问题留到 V2-B 调研和方案确认时统一判断。
