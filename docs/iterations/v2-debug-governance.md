# V2-Debug：AI 辅助开发治理与 Developer Debug Panel v0

## 1. 迭代目标

把三类讨论合并为一个统一治理方案：

- 反过度设计：防止 AI 用兜底、兼容、默认值、提前抽象或未来 runtime 掩盖问题。
- 失败处理与降级策略：允许必要降级，但必须显性化、可追踪、可测试。
- Developer Debug Panel v0：让开发者看到 workflow trace、fallback、mock、schema validation 和边界状态。

本轮是横向基础设施，不改变 V2-C 的反馈权重、否定解释和记忆更新业务目标。

## 2. 边界

本轮包含：

- 更新项目开发流程规则。
- 更新开发计划、验证文档和迭代记录。
- 基于现有 `analysis_logs` 设计最小 debug API。
- 在前端报告页开发环境展示最小 Developer Debug 面板。

本轮不包含：

- Langfuse / LangSmith / OpenTelemetry / Sentry runtime 接入。
- 复杂 dashboard、实时刷新、多用户权限。
- RAG、Agent、MCP、知识图谱、ChromaDB runtime。
- 新增独立观测平台或大规模数据库重构。

## 3. 设计原则

```text
核心链路 fail fast，增强能力 graceful degradation；所有降级必须显性化、可追踪、可测试。
```

开发期默认暴露问题，不为了“让流程继续跑”而吞异常、返回空数组、创建默认对象或跳过 schema 校验。

## 4. 最小数据语义

Developer Debug Panel v0 只需要五类信息：

| 类别 | 来源 | 说明 |
| --- | --- | --- |
| Workflow Trace | `analysis_logs` | 已有 step、status、latency、modelName、promptVersion、errorType |
| Fallback Events | `analysis_logs` 或后续 fallback event | v0 可以为空，但不能静默吞错 |
| Mock Usage | runtime flags | 显示 MockFeatureExtractor / MockEmbeddingClient / heuristic / dev-only 状态 |
| Schema Validation | workflow 结构化步骤 | 显示关键输出 schema 是否通过 |
| Boundary Warnings | 静态边界声明 | 显示 RAG、Agent、MCP、ChromaDB runtime 等 planned / not used |

## 5. API 方案

```text
GET /api/analysis-jobs/{job_id}/debug
```

返回：

```json
{
  "jobId": "job_001",
  "status": "completed",
  "workflowTrace": [],
  "fallbackEvents": [],
  "mockUsage": [],
  "schemaValidation": [],
  "boundaryWarnings": []
}
```

## 6. 验收标准

- 文档中已有统一治理原则。
- 后端 debug API 可以按 job 查询 workflow trace。
- debug API 明确显示 mock usage 和 boundary warnings。
- schema validation 以关键 workflow 输出为粒度显示。
- 前端只在开发环境显示 Developer Debug 面板。
- 未引入外部观测平台或未来版本 runtime。

## 7. 测试计划

- 后端集成测试覆盖 `GET /api/analysis-jobs/{job_id}/debug`。
- 前端执行生产 build，确认开发面板类型检查通过且不会阻断生产构建。

## 8. 复盘记录

实际完成：

- `.cursor/skills/project-development-flow/SKILL.md` 已加入 AI Governance And Debuggability 规则。
- `docs/12-开发任务拆分与里程碑计划.md` 已加入 AI 辅助开发治理约束和 Debug Panel 实施边界。
- `docs/13-验证与评估文档.md` 已加入失败处理与降级策略验收、Developer Debug Panel v0 验收。
- `docs/15-迭代执行记录.md` 已记录本轮横向治理任务。
- 后端新增 `GET /api/analysis-jobs/{job_id}/debug`，返回 workflow trace、fallback events、mock usage、schema validation、boundary warnings。
- 前端报告页在开发环境按 jobId 显示折叠式 Developer Debug 面板。

外部观测工具决策：

```text
Langfuse / LangSmith / OpenTelemetry / Sentry runtime 暂不接入。
等 V3 出现真实 LLM、embedding、RAG、prompt version 和 retrieval trace 后再评估。
```

测试记录：

```text
2026-06-17：
- 后端：python -m pytest，16 passed, 3 warnings。
- 前端：npm run build，通过。
```

剩余风险：

- 当前 fallback events 结构已预留，但现有 workflow 没有显性降级事件，因此 debug API 返回空列表。
- mock usage 和 boundary warnings 在 v0 阶段是静态声明，后续接真实 runtime 时需要改为运行时状态。
- 既有 Pydantic alias warnings 仍为非阻塞遗留问题，本轮未处理。
