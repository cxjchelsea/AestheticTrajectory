# V3-A：Personalized History Retrieval

当前状态：

```text
accepted / manual_validation_passed
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

## 4. 方案选择

### 4.1 检索实现

采用：

```text
PostgreSQL / memory repository + 特征重叠启发式检索
```

原因：

- V2 已有 reports、feedback、profile evidence 数据闭环。
- V3-0 明确 V3-A 可先验证边界，不必先接向量库。
- 与 V2-D report comparison 的纯函数 + repository 模式一致。

### 4.2 历史上下文挂载方式

采用：

```text
workflow step 生成 PersonalHistoryContext，并作为 ReportResponse.historyContext 持久化
```

原因：

- 报告详情只需一次 fetch。
- 历史参考与报告生成时刻绑定，便于 trace 和复盘。
- 不污染 insight.evidenceRefs（仍只指向当前输入）。

### 4.3 前端展示

采用：

```text
ReportDetailPage 新增“历史参考”区块
```

规则：

- 明确区分“历史参考”和“当前输入证据”。
- 展示 summary、items、source refs、direction、disclaimer。
- 无历史时显示 message，不伪装成真实偏好结论。

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
- 报告匹配基于 feature key 重叠。
- `very_me` / `somewhat_me` → positive context。
- `not_me` → negative context。
- `unsure` → neutral context。
- 所有 item 必须有 `sourceRefs`。

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
- 若存在历史 feedback，返回 positive / negative / neutral context items。
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
2026-06-17：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，33 passed, 3 warnings。
- 前端：npm run build，通过。
```

## 10. 人工验收

```text
2026-06-17：
- 用户已完成人工测试，V3-A 历史参考路径测试成功。
- 完成两次分析后，第二份报告详情页出现“历史参考”。
- 历史参考带来源 refs，且与当前输入 evidence 分区展示。
- 第一份报告显示“暂无可参考的历史报告。”
- Developer Debug 中出现 retrieve_personal_history step。
```

## 11. 下一步

```text
用户已完成 V3-A 人工验收；下一步进入 V3-B Aesthetic Knowledge RAG。
```
