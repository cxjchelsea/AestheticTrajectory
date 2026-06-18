# Agent 前沿方向领域设计文档登记表

本文件是 `SKILL.md` 中 **Agent Frontier Design Documents** 的维护登记表。

产品定义来源：`docs/01-产品概念说明书.md` §3。

## 1. 登记原则

- 每个 Agent 前沿方向最终应有一份**语义权威**领域设计文档。
- 不要求项目一开始就全部写完；按版本与子阶段**在合适时机补齐**。
- 已分散在 `04`–`06`、`07`、`11`、`13` 的内容可以保留；领域文档负责**汇总语义、边界、读写规则、治理不变量**，不重复 DDL 与测试日志。

## 2. 文档命名

建议格式：

```text
docs/<NN>-<方向简称>设计文档.md
```

编号从 `19` 起递增（`16`–`18` 保留给版本收口兼容入口）。新增前更新 `docs/00-文档体系说明.md` 与 `docs/README.md`。

## 3. 登记表

| docs/01 | 方向 | 权威文档 | 状态 | 建议触发时机 | 备注 |
| --- | --- | --- | --- | --- | --- |
| §3.1 | Memory / User Model | `docs/19-记忆与用户模型设计文档.md` | **created** | V2 归档 + V3 history/knowledge 边界稳定后 | 含 L4 context 不进 profile 规则 |
| §3.2 | Multimodal Preference Modeling | `docs/20-多模态偏好建模设计文档.md` | **created** | V4-A 验收后 | V4-A 已上升 07/11；音视频解析仍 deferred |
| §3.3 | Temporal User Profiling | 扩展 `19` §10 或独立 `docs/21-时间型用户画像设计文档.md`（拟） | pending | V4-B 方案确认前 | 与 Memory 强相关；可并入 19 若边界清晰 |
| §3.4 | Preference Explanation | `04`–`06` + 可选 `docs/22-偏好解释设计文档.md`（拟） | partial | 当解释链跨 report/RAG/history 且缺单一入口时 | 若 04–06 已足够可不新建 |
| §3.5 | Skill / Capability | `docs/23-Skill与能力沉淀设计文档.md`（拟） | pending | V4-D Agent runtime 方案确认前 | workflow step → skill 沉淀规则 |
| §3.6 | Evaluation / Observability | `docs/13` + 可选 `docs/24-评估与可观测性设计文档.md`（拟） | partial | V4-E 或接入真实 LLM/OTel 前 | V3 已有 baseline metrics + debug trace |
| §3.7 | Governance | `docs/13` + `docs/19` + 可选 `docs/25-治理与安全边界设计文档.md`（拟） | partial | Agent/MCP 扩大治理面之前 | 横切规则；Agent 化前建议独立汇总 |

状态说明：

```text
pending   — 尚未创建权威领域文档
partial   — 权威内容分散在多份文档，尚未汇总为领域入口
created   — 已有权威领域文档并在 00/07/11/13 交叉引用
superseded — 已被合并到其他领域文档（注明目标文档）
```

## 4. 单份领域文档最低结构

1. 文档职责与权威边界（替代哪些、不替代哪些）
2. 一句话定义
3. 核心概念 / 分层 / 对象 taxonomy
4. 读写规则或流程（若适用）
5. 与 Memory / evidence / governance 的接口（若适用）
6. 治理不变量
7. 与版本路线图关系（已实现 / 占位）
8. 实现映射（代码路径，可选）
9. 文档维护规则

## 5. 更新本登记表

在以下事件更新对应行的「状态」与「备注」：

- 新建领域设计文档
- 版本归档后将 iteration 语义上升为权威文档
- 决定合并两个方向到同一文档
- 用户明确决定暂不单独成文（记录原因）
