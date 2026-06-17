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
16 开发收口
iterations 当前迭代任务单
archive 历史归档
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

当前第一阶段已完成 V0 / V1，并进入 V2：

- V0：前端原型 + mock 报告。
- V1：真实输入、底层特征抽象、embedding 抽象、相似性分组、报告、反馈、PostgreSQL 持久化、analysis logs。
- V2-A：历史报告列表与详情回看。
- V2-B：轻量画像数据模型与 profile evidence 已完成代码实现、自动测试、PostgreSQL runtime 验收和前端手动验收。
- V2-C：反馈权重、否定解释和记忆更新已完成自动验证，等待前端人工验收。

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

- `archive/v1/`

当前迭代：

- V2-A 已验收归档：`iterations/v2-a-report-history.md`
- V2-0 已验收归档：`iterations/v2-0-memory-user-model-research.md`
- V2-B 已验收通过：`iterations/v2-b-profile-evidence.md`
- 当前：V2-C 前端人工验收，详见 `iterations/v2-c-feedback-weight-memory-update.md`
