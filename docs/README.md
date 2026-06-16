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
2. `iterations/v1-a-real-feature-extraction.md`
3. 当前 iteration 明确引用的 specs

当前第一阶段只做 V0 / V1：

- V0：前端原型 + mock 报告。
- V1：真实输入、底层特征、embedding、相似性分组、报告、反馈。

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

- `iterations/v1-a-real-feature-extraction.md`
