# Docs-04-11：实现一致性调研与修订

当前状态：

```text
accepted / archived
```

创建日期：

```text
2026-06-16
```

## 1. 本轮定位

本轮是 V2-B 前置的文档一致性收口，不是功能实现阶段。

目标：

```text
核对 docs/04 到 docs/11 是否会误导当前实现或 V2-B 方案设计，并把文档分清楚：当前已实现、V2-B planned、V3+ planned。
```

## 2. 核对范围

本轮核对：

- `docs/04-审美表征体系文档.md`
- `docs/05-AI分析逻辑文档.md`
- `docs/06-输出报告模板文档.md`
- `docs/07-数据结构与系统架构文档.md`
- `docs/08-项目目录结构与代码分层规范.md`
- `docs/09-AI Workflow 编排与任务执行文档.md`
- `docs/10-Prompt Contract 与结构化输出规范.md`
- `docs/11-模块拆分与接口测试文档.md`

当前实现基线：

```text
V1 stable baseline + V2-A report history。
```

已实现能力：

- 输入创建与保存。
- 分析任务创建与查询。
- mock / heuristic 特征抽取。
- embedding 生成与 embedding record 保存。
- 基于当前 job 的相似性分组。
- 报告生成、报告详情、洞察和反馈保存。
- 历史报告列表与详情回看。
- PostgreSQL persistence 与 analysis_logs。

未实现但已设计：

- V2-B `user_profiles` / `profile_items` / `profile_evidence`。
- V2-C feedback 权重与画像更新。
- V2-D 最近报告对比。
- V3 personalized retrieval / RAG。
- V4 Agent / MCP / 知识图谱。

## 3. 主要发现

```text
04 / 05 / 06：
语义方向基本正确，但需要标注当前实现边界，避免长期演化、RAG、画像被误读为已实现。

07：
存在实现不一致：users 字段、embedding_records 表名、analysis_jobs 状态枚举、历史报告 API。

08：
整体符合当前目录结构，但需要说明前端当前是轻量 state route，后端 repository 当前存在 memory/database 双实现。

09：
需要区分当前 workflow 和目标 workflow；ChromaDB reports、历史检索、画像更新属于 planned。

10：
用户画像 prompt contract 仍是旧画像结构，需要改为 evidence-first 的 V2-B contract，并标注 prompt registry 目前未实现。

11：
反馈 rating 枚举与当前代码不一致，需要统一为 not_me / unsure / somewhat_me / very_me；画像模块需要标注 V2-B planned。
```

## 4. 修订原则

- 不把计划能力写成当前实现。
- 不删除长期设计，但必须标注阶段。
- 当前实现以代码、V1-E、V2-A 和 V2-0 design promotion 为准。
- V2-B 只引用已上升到权威文档的 Memory / User Model 规则。
- V3 / V4 内容保留为 planned，不进入 V2-B 实现边界。

## 5. 验收记录

```text
2026-06-16：
结果：通过。

已完成：
- 04 / 05 / 06 增加当前实现边界。
- 07 修正 users、embedding_records、analysis_jobs 状态、历史报告 API 和 planned 标注。
- 08 增加当前目录实现说明。
- 09 区分当前 workflow 和目标 workflow。
- 10 重写 profile.update.v1 的 V2-B evidence-first 输出结构。
- 11 统一 feedback rating，并标注基础用户画像模块为 V2-B planned。
- 12 / 15 同步本轮文档一致性记录。

结论：
docs/04-11 已完成 V2-B 前置一致性收口。下一步可以继续 V2-B 调研和方案确认。
```
