# docs 入口

文档按项目推进顺序编号：

```text
00 入口导航
01 产品定义
02 版本路线
03 MVP 范围
04-06 AI 认知与输出
07-11 工程设计
12 开发执行
13-14 验证与展示
15 迭代记录
16/17/18/21 历史收口兼容入口
19 记忆与用户模型
iterations 当前迭代任务单
archive 历史归档，包括已完成版本的任务拆分、收口清单、验收记录和遗留问题
```

最推荐先读：

1. `00-文档体系说明.md`
2. `01-产品概念说明书.md`
3. `02-版本迭代路线图.md`
4. `03-MVP功能需求文档.md`

准备开发时读：

1. `12-开发任务拆分与里程碑计划.md`
2. 当前 iteration 文档
3. 当前 iteration 明确引用的 specs
4. `19-记忆与用户模型设计文档.md`（涉及 profile、history、knowledge、feedback 时）

已完成版本的任务拆分与收口清单不再从根目录推进，统一查看 `archive/v1/`、`archive/v2/`。

当前第一阶段已完成 V0 / V1 / V2：

- V0：前端原型 + mock 报告。
- V1：真实输入、底层特征抽象、embedding 抽象、相似性分组、报告、反馈、PostgreSQL 持久化、analysis logs。
- V2-A：历史报告列表与详情回看。
- V2-B：轻量画像数据模型与 profile evidence 已完成代码实现、自动测试、PostgreSQL runtime 验收和前端手动验收。
- V2-C：反馈权重、否定解释和记忆更新已完成自动验证和人工复核。
- V2-D：最近两次报告对比与变化说明已完成自动验证和前端人工验收。
- V2-E：稳定验收与记忆治理检查已完成自动验收。
- V2 archive gate：V2 已归档为 Memory / User Model baseline。

不要在第一版提前实现：

- RAG
- Agent
- MCP
- 知识图谱
- 音乐 / 视频
- 复杂长期画像

文档职责冲突时，以 `00-文档体系说明.md` 的“权威来源规则”为准。

附属协作文档：

- `git-commit-message-guide.md`

历史归档：

- `archive/v1/`：V1 stable baseline。
- `archive/v2/`：V2 Memory / User Model baseline，accepted / archived。
- `archive/v3/`：V3 Personalized Retrieval / RAG / Evaluation / Observability baseline，accepted / archived。
- `archive/v4/`：V4 Long-term Personalized Agent baseline，accepted / archived。

当前迭代：

- 当前：**V5-D 已验收，通过进入 V5-E 准备**（`accepted / manual_validation_passed`）
- V5-D：`iterations/v5-d-resilience-observability-tech-debt.md`
- V5-C：`iterations/v5-c-production-mcp-oauth.md`（已验收）
- V5-B：`iterations/v5-b-real-report-runtime.md`（已验收）
- V4-0：`iterations/v4-0-long-term-personalized-agent-research.md`
- V4-A：`iterations/v4-a-runtime-multimodal-foundation.md`（已验收）
- V4-B：`iterations/v4-b-aesthetic-trajectory-temporal-profiling.md`（已验收）
- V4-C：`iterations/v4-c-knowledge-graph-external-rag-runtime.md`（已验收）
- V4-D：`iterations/v4-d-agent-runtime-mcp-integration.md`（已验收）
- V4-E：`iterations/v4-e-evaluation-maturity-governance-validation.md`（已验收）
- V4 归档入口：`archive/v4/`、`21-V4开发收口清单.md`
- 多模态偏好建模：`20-多模态偏好建模设计文档.md`
- 记忆与用户模型：`19-记忆与用户模型设计文档.md`
- V3 归档入口：`archive/v3/`、`18-V3开发收口清单.md`
