# V2-E：稳定验收与记忆治理检查

当前状态：

```text
accepted / automatic_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V2-E 是 V2 Memory / User Model 的最后一个功能验收子阶段，不是 V2 final closure / archive gate。

本轮目标：

```text
验收 V2 记忆系统是否可解释、可修正、不过度推断。
```

V2-E 完成后，才允许进入 V2 final closure / archive gate。

## 2. 上游依据

必须引用：

1. `docs/iterations/v2-0-memory-user-model-research.md`
2. `docs/07-数据结构与系统架构文档.md`
3. `docs/11-模块拆分与接口测试文档.md`
4. `docs/13-验证与评估文档.md`
5. `docs/17-V2开发收口清单.md`

V2 子阶段顺序：

```text
V2-0 -> V2-A -> V2-B -> V2-C -> V2-D -> V2-E -> V2 final closure / archive
```

## 3. 问题定义

本轮要回答：

```text
当前 V2 轻量画像、反馈修正和最近变化能力，是否符合 evidence-first、用户反馈优先、不过度推断和可治理的要求？
```

具体问题：

- 每个 profile item 是否都有 evidence。
- `not_me` 是否不会进入正向画像。
- `unsure` 是否不会强化正向 summary。
- 修改同一 insight feedback 后，画像是否只反映最新反馈。
- 被否定解释是否不会反复作为正向倾向出现。
- 页面文案是否不输出人格、心理、能力或命运判断。

## 4. 本轮边界

本轮包含：

- profile evidence coverage 检查。
- rejected / uncertain / conflict 语义检查。
- feedback influence 检查。
- 最近变化文案治理检查。
- 必要的测试补充和文档同步。

本轮不包含：

- V3 personalized retrieval。
- RAG / Agent / MCP。
- ChromaDB runtime 写入或查询。
- 真实 LLM / vision / embedding runtime。
- 长期趋势图、周报、月报。
- 自动推荐或消费引导。
- V2 final archive。

## 5. 验收标准

V2-E 通过需要满足：

- profile evidence coverage 可被测试或检查。
- `not_me` 生成 negative evidence，不进入正向 summary。
- `unsure` 生成 uncertain evidence，不强化正向 summary。
- feedback 更新不重复累计。
- 被否定解释不作为正向倾向反复强化。
- 画像和最近变化页面不输出人格、心理、能力或命运判断。
- V2 遗留问题和验收核对表能清楚区分 `resolved`、`pending_validation`、`carry_over`、`blocking`。

## 6. AI 生成计划

```text
1. 复核现有 profile builder 和 feedback tests。
2. 补充或调整 V2-E 治理检查测试。
3. 必要时补充小型检查脚本或测试 helper。
4. 复核前端画像页和最近变化页文案。
5. 运行后端测试、前端 build、lint。
6. 同步 12 / 13 / 15 / archive/v2 文档。
7. V2-E 通过后，再进入 V2 final closure / archive gate。
```

禁止 AI 自行决定：

- 不提前把 V2 标记为 archived。
- 不用 final closure 替代 V2-E。
- 不新增 V3 / V4 runtime。
- 不把用户反馈包装成永久人格判断。

## 7. 当前结论

```text
V2-E 已完成自动治理检查。
本轮只完成记忆治理验收，不进入 V2 final closure。
```

## 8. 实现记录

新增自动测试：

```text
backend/app/tests/unit/test_memory_governance_validation.py
```

覆盖：

- profile items 必须有 evidence，sourceCount 与 evidence 数量一致。
- profile summary 和 evidence note 不包含人格、心理、能力、命运、灵魂、绝对化判断等诊断式表达。
- `not_me` 生成 rejected item 和 negative evidence，不进入正向画像。
- 被否定解释不会作为正向 profile item 复现。
- `unsure` 保留为 uncertain evidence，不强化 summary。
- feedback 更新后的 profile snapshot 只使用最新 feedback，不重复累计。

## 9. 验证记录

```text
2026-06-17：
- 后端定向测试：python -m pytest app/tests/unit/test_memory_governance_validation.py，4 passed。
- 后端完整测试：REPOSITORY_BACKEND=memory python -m pytest，30 passed, 3 warnings。
- 前端：npm run build，通过。
- Lints：无新增错误。
```

## 10. 当前结论

```text
V2-E 自动验收通过。
下一步可以进入 V2 final closure / archive gate，但不能自动把 V2 标记为 archived。
```
