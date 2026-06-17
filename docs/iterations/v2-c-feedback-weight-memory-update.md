# V2-C：反馈权重、否定解释和记忆更新

当前状态：

```text
implemented / automatic_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V2-C 是 V2 Memory / User Model 的第二个实现子阶段。

本轮目标：

```text
在 V2-B 轻量画像和 profile evidence 基础上，确认 insight feedback 如何影响画像证据、画像条目状态和用户记忆更新。
```

本轮完成后，用户应该能看到：

```text
用户对洞察的 very_me / somewhat_me / unsure / not_me 反馈，会以不同方向和权重进入 profile evidence，并影响 profile item 的状态、权重、置信度和摘要表达。
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v2-0-memory-user-model-research.md`
2. `docs/iterations/v2-b-profile-evidence.md`
3. `docs/07-数据结构与系统架构文档.md`
4. `docs/11-模块拆分与接口测试文档.md`
5. `docs/13-验证与评估文档.md`
6. `docs/12-开发任务拆分与里程碑计划.md`

继承规则：

```text
先 evidence，后 profile。
先用户反馈，后模型推断。
不把被否定解释作为正向记忆。
不把单次输入固化为长期偏好。
只描述审美倾向，不做人格诊断。
开发期 fail fast，不用静默 fallback 掩盖错误。
```

## 3. 问题定义

本轮要解决：

```text
用户反馈如何改变轻量画像，而不让系统误把模型解释固化为用户偏好？
```

拆成具体问题：

- `very_me` 是否应该强正向强化 profile item。
- `somewhat_me` 是否应该弱正向强化 profile item。
- `unsure` 是否应该保留为 uncertain evidence，但不强化画像。
- `not_me` 是否应该生成 negative evidence，并阻止相关解释进入正向 summary。
- 用户反馈和模型 feature evidence 冲突时，是否应该记录 conflict，而不是覆盖旧画像。
- 当前 profile builder 是否需要从“只读聚合”调整为“反馈优先的权重更新规则”。

## 4. 本轮边界

本轮包含：

- 反馈 rating 到 evidence direction / weight_delta 的规则确认。
- profile item 状态更新规则确认。
- negative / uncertain / conflict evidence 的处理规则确认。
- 被否定解释不进入正向画像摘要。
- 后端 profile builder / repository / service 的最小实现调整。
- 后端测试覆盖反馈权重和否定解释治理。
- 前端画像页如有必要，优化 feedback evidence 的可读展示。

本轮不包含：

- 最近两次报告对比与变化说明；该能力保留给 V2-D。
- 长期趋势图、周报 / 月报或审美轨迹可视化。
- 真实 LLM / RAG / Agent / MCP。
- ChromaDB runtime 写入。
- 复杂机器学习、推荐系统、时间衰减模型。
- 用户手动编辑 / 删除 / 隐藏 profile item UI。

## 5. 权威设计文档影响判断

```text
本轮是否改变长期架构 / 数据模型 / API 契约 / workflow / prompt contract / 模块边界 / 验证指标 / 治理规则：
部分改变。

数据模型：
不新增表。继续使用 V2-B 已实现的 user_profiles / profile_items / profile_evidence。

API：
默认不新增 API。继续使用 GET /api/users/{user_id}/profile 和 POST /api/insights/{insight_id}/feedback。

长期规则：
需要把 V2-C 实际采用的反馈权重、状态更新和冲突处理规则同步到 07 / 11 / 13，前提是实现阶段确实改变当前规则。
```

当前方案确认阶段先不机械更新 07 / 11 / 13；实现完成后再根据实际代码是否改变长期规则决定是否上升。

## 6. 轻量调研记录

### 6.1 Explicit / implicit feedback 与负向信号

来源名称：Recommending based on Implicit Feedback；Understanding and Modeling Passive-Negative Feedback for Short-video Sequential Recommendation

来源类型：推荐系统反馈建模 / 负向反馈研究

链接或出处：

- `https://web-ainf.aau.at/pub/jannach/files/BookChapter_Social_Information_Access_2018.pdf`
- `https://arxiv.org/abs/2308.04086`

采用结论：

```text
显式反馈比隐式行为更适合解释给用户，也更适合进入可审查画像。
负向反馈是高价值信号，不能简单忽略；但也不能直接删除历史证据，应作为 negative evidence 参与治理。
```

不能照搬：

- 本项目不做推荐排序。
- 不做负采样、召回模型或序列推荐。
- 不把 not_me 转成推荐约束，只用于画像治理和避免误强化。

### 6.2 反馈循环与误强化风险

来源名称：Breaking Feedback Loops in Recommender Systems with Causal Inference

来源类型：推荐系统反馈循环风险研究

链接或出处：`https://dl.acm.org/doi/full/10.1145/3728372`

采用结论：

```text
系统如果只强化已经出现的正向信号，容易形成反馈循环和偏好固化。
V2-C 必须让 not_me / unsure 能阻止或削弱画像，而不是只累加 positive evidence。
```

不能照搬：

- 不实现因果校正算法。
- 不做推荐训练数据校正。
- 只采用“显式记录负向和不确定证据”的治理思想。

### 6.3 短期 / 长期偏好分层

来源名称：Recommender System Based on Temporal Models: A Systematic Review；A Ranking Recommendation Algorithm Based on Dynamic User Preference

来源类型：Temporal user profiling / dynamic preference modeling

链接或出处：

- `https://www.mdpi.com/2076-3417/10/7/2204`
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC9698759/`

采用结论：

```text
用户偏好应区分 short-term / long-term。近期反馈可以影响 recent 或 uncertain 状态，但不应直接覆盖 stable 倾向。
V2-C 不实现时间衰减模型，只确认反馈如何影响 profile item 状态。
```

不能照搬：

- 不做 exponential decay、attention fusion 或长短期向量融合。
- 不把最近两次报告变化写进 V2-C；该能力留给 V2-D。

## 7. 方案确认

V2-C 采用以下最小规则：

```text
very_me:
- direction = positive
- weight_delta = +0.4
- 可以支持 stable，但必须仍保留 evidence refs

somewhat_me:
- direction = positive
- weight_delta = +0.2
- 弱正向证据，可支持 recent 或累积成 stable

unsure:
- direction = uncertain
- weight_delta = 0.0
- 不强化画像，只保留待观察

not_me:
- direction = negative
- weight_delta = -0.5
- 生成 rejected 或降低相关 profile item 权重
- 不进入正向 summary
```

状态更新规则：

```text
rejected:
- negative evidence 存在，且没有足够用户确认的 positive evidence 抵消。

uncertain:
- 只有 uncertain evidence，或正负证据不足以形成方向。

recent:
- 有正向 evidence，但来源较少或主要来自近期报告。

stable:
- 至少 2 个正向 evidence，或 1 个 very_me 强反馈 evidence。

conflict:
- 同一 profile item 同时存在明确 positive 和 negative evidence，后续实现可记录 conflict evidence 或保持 item 为 uncertain / recent，并在 note 中说明冲突。
```

摘要生成规则：

```text
profile summary 只使用 stable / recent 且 weight > 0 的 item。
rejected / uncertain / hidden / deleted 不进入正向 summary。
存在被否定或不确定 evidence 时，可以在开发者调试或 evidence 列表展示，但用户摘要不把它包装成偏好。
```

## 8. 数据模型设计

本轮不新增表。

继续使用：

```text
user_profiles
profile_items
profile_evidence
insight_feedback
```

需要重点保证：

- `profile_evidence.direction` 可以保存 `positive / negative / uncertain / conflict`。
- `profile_evidence.weight_delta` 可以保存正负权重。
- `profile_items.status` 可以保存 `stable / recent / rejected / uncertain / inactive / hidden / deleted`。
- feedback evidence 的 `evidence_id` 指向 `insight_feedback.id`。

## 9. API 设计

本轮默认不新增 API。

继续使用：

```text
POST /api/insights/{insight_id}/feedback
GET /api/users/{user_id}/profile
```

目标行为：

```text
用户提交 feedback 后，再查询 profile，应能看到 feedback evidence 已影响 profile item。
```

异常边界：

- insight 不存在必须失败，不创建 orphan feedback。
- feedback rating 非法必须失败。
- profile evidence 无法关联时必须暴露问题，不静默跳过。

## 10. 前端展示边界

本轮前端可以小改：

- 确认 profile 页面能清楚展示 feedback evidence。
- 将 negative / uncertain evidence 显示为“用户反馈修正”或“待确认信号”，避免内部字段裸露。
- 不做复杂权重可视化。
- 不做手动编辑 / 删除 profile item。
- 不做最近两次报告对比 UI。

## 11. 测试与验收

后端测试：

- `very_me` 生成 positive evidence，weight_delta 为强正向。
- `somewhat_me` 生成 positive evidence，weight_delta 为弱正向。
- `unsure` 生成 uncertain evidence，不强化画像。
- `not_me` 生成 negative evidence，并阻止相关解释进入正向 summary。
- 单次无反馈高层解释不能直接成为 `stable`。
- 正负冲突时不能直接覆盖旧画像，至少保留可追踪 evidence。
- insight 不存在时 feedback 不应保存为 orphan feedback。

前端验收：

- 提交 `not_me` 后，画像页不会把该洞察作为正向倾向展示。
- feedback evidence 的文案用户可读。
- 页面不输出人格、心理或能力诊断。

文档验收：

- 本任务单记录调研与方案确认。
- 实现完成后更新 `07 / 11 / 13 / 12 / 15` 的实际状态。
- 如果未改变长期设计，iteration 文档记录“不需要上升权威文档”。

## 12. AI 生成计划

实现阶段建议顺序：

```text
1. 阅读 profile_builder 当前反馈映射和 profile repository。
2. 收敛 feedback_signal / status / summary 规则。
3. 增加 profile builder 单元测试，先覆盖 very_me / somewhat_me / unsure / not_me。
4. 增加 rejected / uncertain 不进入正向 summary 的测试。
5. 增加 API flow 或 repository 测试，覆盖 feedback 后 profile 变化。
6. 如有必要，优化 ProfilePage 文案和 evidence 展示。
7. 运行后端 pytest 和前端 build。
8. 更新本任务单实现记录与 15 执行记录。
```

禁止 AI 自行决定：

- 不新增 feedback rating 枚举。
- 不新增 profile 状态枚举。
- 不引入机器学习权重模型。
- 不新增报告对比 API。
- 不提前实现 V2-D / V3 / V4。
- 不用 fallback 掩盖 feedback / profile evidence 关联错误。

## 13. 当前结论

```text
V2-C 方案已确认：
本轮聚焦反馈权重、否定解释和记忆更新。
最近两次报告对比不放入 V2-C，保留为 V2-D。
默认不新增数据库表和 API，优先收敛 profile builder 的反馈治理规则、测试和前端 evidence 表达。
```

## 14. 实现记录

2026-06-17 已完成：

```text
Backend:
- 收敛 profile_builder 的反馈权重与状态规则。
- very_me / somewhat_me 作为正向 evidence。
- unsure 作为 uncertain evidence，不强化画像。
- not_me 作为 negative evidence，负向或净负权重条目标记为 rejected。
- 正负冲突时不直接升为 stable，保留正负 evidence 可追踪。
- profile summary 只使用 stable / recent 且 weight > 0 的正向条目。
- feedback service 增加 insight 存在性校验，避免 orphan feedback。
- memory / database feedback repository 均支持 insight_exists。
- feedback API 对不存在的 insight 返回 404。

Frontend:
- 报告结果页增加返回首页和查看轻量画像入口。
- 画像页将 stable / recent 正向倾向与 rejected / uncertain 修正记录分区展示。
- not_me / unsure 不进入正向画像区域，但会在“你已否定或待确认的解释”中保留可追溯 evidence。

Testing:
- 新增 profile_builder 单元测试，覆盖 very_me / somewhat_me / unsure / not_me。
- 新增 conflict feedback 测试，确认正负证据不会直接生成 stable。
- 扩展 API flow，确认不存在的 insight 不能保存 feedback。
```

2026-06-17 反馈重复累计修正：

```text
Backend:
- feedback service 支持读取当前 insight feedback。
- 同一 user_id + insight_id 再次反馈时更新原 feedback id，不新增重复记录。
- memory / database repository 保存 feedback 时清理同一目标的旧重复记录。
- profile builder 继续保证同一条 feedback 不会因重复 mock insight id 被多次归因。

Frontend:
- 反馈面板进入历史报告时读取已保存 feedback 并高亮当前选择。
- 再次选择反馈会更新这条 feedback，界面提示不会重复累计。

Testing:
- API flow 覆盖先反馈、再修改、画像中只使用更新后的 feedback evidence。
- database repository 覆盖持久化层同一目标 feedback 更新语义。
```

自动验证：

```text
后端：python -m pytest，20 passed, 3 warnings。
前端：npm run build，通过。
Lints：无新增错误。
前端修正后复验：npm run build，通过。
反馈更新修正后复验：python -m pytest，23 passed, 3 warnings；npm run build，通过；Lints 无新增错误。
```

权威文档影响判断：

```text
不新增数据库表。
新增 GET /api/insights/{insight_id}/feedback，用于前端读取当前用户对该 insight 的最新反馈。
不新增 feedback rating 枚举。
不新增 profile item status 枚举。
本轮实际实现与 V2-0 / V2-B 已上升到 07 / 11 / 13 的规则一致。
无需新增长期架构章节；只需要在执行记录和验证记录中补充 V2-C 自动验证结果与反馈更新语义。
```

剩余人工验收：

```text
需要用户在前端手动确认：
1. 提交 not_me 后，该洞察出现在“你已否定或待确认的解释”，不进入正向“倾向条目”。
2. 报告结果页可以返回首页，也可以直接进入轻量画像页。
3. feedback evidence 文案仍然用户可读。
4. 页面不输出人格、心理或能力诊断。
```
