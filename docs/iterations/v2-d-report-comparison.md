# V2-D：最近报告对比与变化说明

当前状态：

```text
accepted / frontend_manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V2-D 是 V2 Memory / User Model 的收口子阶段之一。

本轮目标：

```text
在 V2-A 历史报告、V2-B 轻量画像、V2-C feedback evidence 基础上，让用户查看最近两次报告之间的可追溯变化说明。
```

本轮完成后，用户应该能看到：

```text
最近两次输入中哪些底层特征、解释或洞察方向发生了变化、重复出现或减弱。
```

## 2. 上游依据

必须引用：

1. `docs/02-版本迭代路线图.md`
2. `docs/06-输出报告模板文档.md`
3. `docs/11-模块拆分与接口测试文档.md`
4. `docs/13-验证与评估文档.md`
5. `docs/archive/v2/V2-遗留问题.md`
6. `docs/17-V2开发收口清单.md`

继承规则：

```text
只描述最近两次输入中出现的方向变化。
不把两次输入上升为长期人格、心理、能力或命运变化。
每条变化说明必须能追溯到 report / feature / insight evidence。
不提前实现 RAG、Agent、趋势图、周报、月报或复杂时间衰减模型。
```

## 3. 问题定义

本轮要解决：

```text
系统如何基于已有历史报告，生成最近两次报告之间的轻量变化说明？
```

拆成具体问题：

- 历史报告不足两份时如何返回空状态。
- 最近两份报告如何排序和取数。
- 哪些字段适合做最小对比：lowLevelFeatures、possibleInterpretations、insights。
- 如何生成新增、减弱、重复出现的变化项。
- 如何保证变化说明可追溯且不过度解释。

## 4. 本轮边界

本轮包含：

- 最近两次报告对比 read model。
- 最近两次报告对比 API。
- 基于 report_json 的 feature / interpretation / insight 对比。
- 历史报告页进入“最近变化”视图。
- 历史不足时的明确空状态。
- 自动测试和前端 build 验证。

本轮不包含：

- 长期趋势图。
- 周报 / 月报。
- 自动推送变化提醒。
- RAG / Agent / MCP。
- ChromaDB runtime 写入或查询。
- 真实 LLM 变化总结。
- 新增持久化表。
- 用户手动编辑变化记录。

## 5. 权威设计文档影响判断

```text
本轮是否改变长期架构 / 数据模型 / API 契约 / workflow / prompt contract / 模块边界 / 验证指标 / 治理规则：
部分改变。

数据模型：
不新增表。复用 aesthetic_reports.report_json。

API：
新增只读 API：GET /api/users/{user_id}/reports/comparison/latest。

模块边界：
实现 11 中已规划的“报告对比与审美轨迹模块”的最小 V2-D 切片。

治理规则：
沿用 13 中“近期变化不能写成人格改变”的表达规则。
```

实现完成后需要同步 `15`、`12`、`archive/v2`；是否更新 `07 / 11 / 13` 取决于最终 API 契约是否作为长期设计固定下来。

## 6. 轻量调研记录

### 6.1 Temporal user profiling

采用结论：

```text
变化说明应区分 recent signal 与 stable preference。
V2-D 只比较最近两次报告，不做长期趋势建模。
```

### 6.2 Explainable change summaries

采用结论：

```text
变化说明必须绑定证据来源，避免只生成抽象结论。
“变化”应表达为输入集合之间的可观察差异，而不是用户人格改变。
```

### 6.3 Product boundary

采用结论：

```text
V2-D 的变化说明应放在历史报告语境中，作为回看辅助。
不做主动通知、推荐或长期轨迹可视化。
```

## 7. 方案确认

V2-D 采用以下最小方案：

```text
新增 read-only response：
- previousReport
- currentReport
- featureChanges
- interpretationChanges
- summary
- message
- disclaimer

计算方式：
- 从最近两份 ReportResponse 中提取 feature key/value。
- 对比 current 与 previous 的出现次数。
- 生成 new / increased / decreased / repeated 四类 feature changes。
- 对比 possibleInterpretations.name 与 insights.title，生成新增、延续或减弱的解释变化。
```

## 8. API 设计

```text
GET /api/users/{user_id}/reports/comparison/latest
```

行为：

- 最近报告不足两份：返回 `comparison: null` 等价空状态信息。
- 最近报告不少于两份：返回最近两份报告的对比结果。

## 9. 前端展示边界

前端新增：

- 历史页进入“最近变化”入口。
- 最近变化页 / 视图展示：
  - 对比的两份报告。
  - 变化摘要。
  - 底层特征变化。
  - 解释 / 洞察方向变化。
  - disclaimer。

不展示：

- 长期趋势折线图。
- 周报 / 月报。
- 推荐或行动建议。

## 10. 测试与验收

后端测试：

- 历史不足两份时返回明确 message。
- 最近两份报告可生成 feature changes。
- 变化说明包含 report evidence。
- summary 不输出人格、心理或能力诊断。

前端验收：

- 历史页可以进入最近变化。
- 报告不足时展示明确空状态。
- 有两份报告时展示变化摘要和证据。
- 页面不输出人格、心理或能力诊断。

## 11. AI 生成计划

```text
1. 新增 comparison schema。
2. 新增 comparison builder 纯函数。
3. 扩展 memory/database report repository，支持取最近两份报告。
4. 扩展 ReportService 和 reports route。
5. 增加后端测试。
6. 增加前端 types、API client、页面和路由入口。
7. 运行后端 pytest、前端 build、lint。
8. 同步 12 / 15 / archive/v2 文档状态。
```

禁止 AI 自行决定：

- 不新增数据库表。
- 不新增推荐、RAG、Agent、趋势图或周报。
- 不把变化写成人格、心理或能力变化。
- 不把历史不足包装成变化结论。

## 12. 当前结论

```text
V2-D 方案已确认：
本轮只实现最近两次报告对比与变化说明。
复用已有 report_json，不新增持久化表。
```

## 13. 实现记录

后端已完成：

- 新增 `ReportComparisonResponse`、`ReportFeatureChange`、`ReportInterpretationChange`。
- 新增 `build_latest_report_comparison` 纯函数。
- `ReportRepository` / `DatabaseReportRepository` 支持按用户取最近报告。
- `ReportService` 提供 `compare_latest_reports`。
- 新增 API：`GET /api/users/{user_id}/reports/comparison/latest`。

前端已完成：

- `ReportComparisonResponse` 等类型。
- `getLatestReportComparison` API client。
- `ReportComparisonPage`。
- 历史报告页“查看最近变化”入口。
- `comparison` route。

文档已同步：

- `docs/11-模块拆分与接口测试文档.md`
- `docs/12-开发任务拆分与里程碑计划.md`
- `docs/13-验证与评估文档.md`
- `docs/15-迭代执行记录.md`
- `docs/archive/v2/V2-遗留问题.md`
- `docs/archive/v2/V2-验收核对表.md`

## 14. 验证记录

```text
2026-06-17：
- 后端：REPOSITORY_BACKEND=memory python -m pytest，26 passed, 3 warnings。
- 前端：npm run build，通过。
- Lints：无新增错误。
```

## 15. 待人工验收

```text
- 历史页可以进入“最近变化”。
- 历史不足两份时展示明确空状态。
- 有两份报告时展示最近两次报告、变化摘要、feature changes、interpretation changes 和 evidence refs。
- 页面不输出人格、心理或能力诊断式表达。
```

人工验收结果：

```text
2026-06-17：
- 用户已完成 V2-D 前端人工测试。
- 最近报告对比路径测试成功。
- 分析页 React StrictMode 下卡在“正在保存输入样本”的问题已修复并通过前端 build。
```
