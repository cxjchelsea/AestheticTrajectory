# V2-B：轻量画像数据模型与 profile evidence

当前状态：

```text
accepted / frontend_manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮定位

V2-B 是 V2 Memory / User Model 的第一个实现子阶段。

本轮目标：

```text
在 V2-0 版本级规则基础上，确认轻量画像数据模型和 profile evidence 的最小闭环方案。
```

本轮完成后，用户可以做什么：

```text
方案确认后，下一步实现时用户应能查看一个只读轻量画像，并看到每个画像倾向对应的 evidence refs。
```

## 2. 上游依据

必须引用：

1. `docs/07-数据结构与系统架构文档.md`
2. `docs/11-模块拆分与接口测试文档.md`
3. `docs/13-验证与评估文档.md`
4. `docs/12-开发任务拆分与里程碑计划.md`
5. `docs/iterations/v2-0-memory-user-model-research.md`
6. `docs/iterations/docs-04-11-implementation-alignment.md`

继承规则：

```text
先 evidence，后 profile。
先用户反馈，后模型推断。
先轻量画像，后长期 Agent。
只描述审美倾向，不做人格诊断。
不把单次输入固化为长期偏好。
不把被否定解释作为正向记忆。
```

## 3. 问题定义

本轮要解决：

```text
系统如何把历史报告、底层特征、洞察和反馈组织成可追溯的轻量画像？
```

拆成具体问题：

- `user_profiles`、`profile_items`、`profile_evidence` 是否作为 V2-B 最小数据结构。
- profile item 的最小字段和状态枚举如何确定。
- profile evidence 如何引用输入特征、报告、解释、洞察和反馈。
- stable / recent / rejected / uncertain 的判定边界如何在 V2-B 保持简单。
- V2-B 是否只做只读画像和 evidence 查询，不做复杂更新策略。
- 前端是否先展示 profile summary + evidence list。

## 4. 本轮不做

- 不实现 V2-C 的复杂反馈权重。
- 不实现自动遗忘。
- 不实现最近两次报告对比。
- 不实现推荐、RAG、Agent Runtime、MCP。
- 不把 ChromaDB 作为业务记忆来源。
- 不引入复杂登录权限系统。
- 不做人格、心理、能力或命运判断。

## 5. 权威设计文档影响判断

```text
本轮是否改变长期架构 / 数据模型 / API 契约 / workflow / prompt contract / 模块边界 / 验证指标 / 治理规则：
是。V2-B 将 V2-0 的 planned 数据模型收敛为具体实现方案，影响数据库 migration、repository/service/API、前端展示和测试验收。

需要更新哪些权威文档：
本轮方案确认已同步：
- `docs/07-数据结构与系统架构文档.md`：补充 V2-B profile API。
- `docs/11-模块拆分与接口测试文档.md`：补充基础用户画像模块接口边界。

实现完成后还需要同步：
- `docs/07-数据结构与系统架构文档.md`：实际 migration 字段。
- `docs/13-验证与评估文档.md`：实际测试结果和验收记录。
- `docs/15-迭代执行记录.md`：实现与测试记录。
```

## 6. 外部调研记录

### 6.1 Transparent and Scrutable User Models

来源名称：Transparent and Scrutable Recommendations Using Natural Language User Profiles

来源类型：论文 / 可解释推荐与自然语言用户画像

链接或出处：`https://aclanthology.org/2024.acl-long.753.pdf`

采用结论：

```text
用户画像应当是人可读、可审查、可修改的，而不是只存在于不可解释 embedding 中。
V2-B 应优先生成轻量自然语言 summary 和结构化 profile item，便于用户理解系统如何描述自己。
```

不能照搬：

- 不做推荐排序。
- 不训练或微调模型。
- 不让用户直接编辑复杂画像权重。

### 6.2 Explainable Temporal User Profiling

来源名称：Towards Explainable Temporal User Profiling with LLMs / Temporal User Profiling with LLMs

来源类型：论文 / 短期与长期偏好建模

链接或出处：

- `https://arxiv.org/pdf/2505.00886`
- `https://arxiv.org/pdf/2508.08454`

采用结论：

```text
画像需要区分 stable long-term preference 和 recent short-term interest。
V2-B 应保留 stable / recent 状态，但先不实现复杂时间衰减或 attention fusion。
```

不能照搬：

- 不生成短期/长期 embedding 融合模型。
- 不引入 BERT / attention 训练。
- 不做推荐预测。

### 6.3 Preference Feedback Signals

来源名称：Preference Elicitation with Soft Attributes / Negative Preferences in Recommender Systems / Explicit Context Feedback

来源类型：偏好反馈、负向偏好、交互式推荐调研

链接或出处：

- `https://liralab.usc.edu/pdfs/publications/biyik2023preference.pdf`
- `https://link.springer.com/article/10.1007/s10844-022-00705-9`
- `https://arxiv.org/html/2605.29141v1`

采用结论：

```text
正向、负向和不确定反馈都应保存为不同方向的 evidence。
负向偏好不应简单删除，而应作为约束和防止重复强化的信号。
```

不能照搬：

- V2-B 不做贝叶斯偏好估计。
- V2-B 不做复杂 soft attribute query。
- V2-B 不把负向 evidence 直接转成推荐约束。

### 6.4 Evidence-grounded Explanations

来源名称：Explainable recommender systems with path evidence / user model transparency

来源类型：可解释推荐、evidence provenance、scrutable user model

链接或出处：

- `https://research.google/pubs/transparent-scrutable-and-explainable-user-models-for-personalized-recommendation/`
- `https://www.sciencedirect.com/science/article/abs/pii/S0950705126009627`

采用结论：

```text
解释必须引用具体 evidence，profile item 不应孤立存在。
V2-B 的每个 profile item 必须至少有一个 profile evidence，且 evidence 要能追溯到 feature / report / interpretation / insight / feedback。
```

不能照搬：

- 不做知识图谱 path evidence。
- 不引入 KG / RAG。
- 不把 evidence 用于推荐解释，只用于画像可解释性。

### 6.5 Profiling Governance

来源名称：GDPR Recital 71 / Article 22 / ICO automated decision-making and profiling guidance

来源类型：隐私治理、自动化决策与 profiling 规则

链接或出处：

- `https://gdpr-info.eu/recitals/no-71/`
- `https://gdpr-info.eu/art-22-gdpr/`
- `https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/rights-related-to-automated-decision-making-including-profiling/`

采用结论：

```text
用户画像需要透明说明数据来源、用途和影响。
V2-B 不做自动化重大决策，不把画像用于消费引导或推荐，只做可查看的审美倾向摘要。
数据结构预留 hidden / deleted 状态，后续支持用户修正和删除。
```

不能照搬：

- 当前不是完整法律合规实现。
- V2-B 不做完整权限、审计和删除工作流。
- V2-B 不处理儿童、合同或法律授权场景。

## 6.6 调研总原则

V2-B 采用：

```text
1. Profile item 必须有 evidence。
2. Evidence 是事实记录，profile item 是聚合结果。
3. 用户反馈优先于模型推断。
4. stable 和 recent 必须区分。
5. rejected 只用于避免重复强化，不进入正向画像。
6. uncertain 不强化画像，只保留待观察。
7. 画像只读展示，不做推荐和自动决策。
8. 先实现可追溯，再考虑权重和自动更新。
```

## 7. 方案确认

V2-B 采用以下方案：

```text
新增 PostgreSQL 业务表：
- user_profiles
- profile_items
- profile_evidence

新增后端能力：
- profile repository
- profile service
- profile evidence 聚合逻辑
- GET /api/users/{user_id}/profile

新增前端能力：
- ProfilePage
- 从首页和历史页进入画像页
- 展示 profile summary、profile items、evidence refs

本轮实现策略：
- 先用已有历史报告、features、interpretations、insights、feedback 生成只读画像。
- 不做复杂权重和自动遗忘。
- 不接 ChromaDB。
- 不接 RAG / Agent。
```

方案选择理由：

- 三表结构能把 evidence 和 profile item 分离，符合 V2-0 的 evidence-first 规则。
- 只读 API 降低 V2-B 风险，把反馈权重和更新策略留给 V2-C。
- 前端先展示 evidence refs，能快速验证“为什么这样判断”是否成立。

## 8. 数据模型设计

### 8.1 user_profiles

```text
id
user_id
summary
version
created_at
updated_at
```

约束：

- `user_id` 建索引。
- V2-B 可以先保持每个 user 一个 active profile。
- `summary` 必须由 profile items 聚合，不允许无 evidence 的高级词。

### 8.2 profile_items

```text
id
profile_id
key
label
status
weight
confidence
source_count
last_seen_at
created_at
updated_at
```

status：

```text
stable
recent
rejected
uncertain
inactive
hidden
deleted
```

V2-B 最小规则：

- `stable`：至少 2 个正向 evidence，或 1 个强正向 feedback evidence。
- `recent`：来自最近报告，但证据不足以稳定化。
- `rejected`：来自 `not_me` 或明确负向 evidence，不进入正向 summary。
- `uncertain`：来自 `unsure` 或模型低置信 evidence，不强化画像。
- `inactive / hidden / deleted`：V2-B 先预留状态，不实现完整 UI 操作。

### 8.3 profile_evidence

```text
id
profile_item_id
evidence_type
evidence_id
direction
weight_delta
note
created_at
```

evidence_type：

```text
feature
report
interpretation
insight
feedback
```

direction：

```text
positive
negative
uncertain
conflict
```

V2-B 证据规则：

- feature / report / interpretation / insight evidence 可以来自模型分析结果。
- feedback evidence 来自用户显式反馈，优先级高于模型 evidence。
- 每个 profile item 至少 1 条 evidence。
- `not_me` 必须生成 negative evidence。
- `unsure` 必须生成 uncertain evidence。
- `somewhat_me` 生成弱 positive evidence。
- `very_me` 生成强 positive evidence。

### 8.4 暂不采用

- 不把 profile 只塞进 `aesthetic_reports.report_json`。
- 不把 profile 只存在前端。
- 不把 profile 只存在 ChromaDB。
- 不新增独立向量画像表。
- 不做复杂 event sourcing。

## 9. API 设计

### 9.1 查询用户画像

```text
GET /api/users/{user_id}/profile
```

用途：

- 查询当前用户的只读轻量画像。
- 返回 summary、items 和 evidence refs。
- 如果没有足够 evidence，返回 empty profile。

Response：

```json
{
  "userId": "user_001",
  "profile": {
    "id": "profile_001",
    "summary": "系统观察到你近期多次输入中出现低饱和、人物缺席和结构化冷感。",
    "version": "v2-b",
    "items": [
      {
        "id": "profile_item_001",
        "key": "low_saturation",
        "label": "低饱和倾向",
        "status": "stable",
        "weight": 0.72,
        "confidence": 0.68,
        "sourceCount": 3,
        "lastSeenAt": "2026-06-17T00:00:00Z",
        "evidence": [
          {
            "id": "profile_evidence_001",
            "evidenceType": "feature",
            "evidenceId": "feature_001",
            "direction": "positive",
            "note": "多次报告中出现 low_saturation。"
          }
        ]
      }
    ],
    "updatedAt": "2026-06-17T00:00:00Z"
  }
}
```

空状态：

```json
{
  "userId": "user_001",
  "profile": null,
  "message": "还没有足够证据生成轻量画像。"
}
```

### 9.2 本轮不新增

- 不新增手动编辑 profile item API。
- 不新增删除 / 隐藏 profile item API。
- 不新增 profile refresh 异步任务 API。
- 不新增推荐相关 API。

## 10. 前端展示边界

V2-B 前端只展示：

- 画像摘要。
- 画像条目列表。
- 每个条目的状态、置信度、证据数量。
- evidence refs 的可读说明。
- 空状态：证据不足时不强行生成画像。

不展示：

- 复杂权重调节。
- 手动删除 / 隐藏按钮。
- 推荐结果。
- RAG 知识解释。
- Agent 记忆管理 UI。

## 11. 测试与验收

后端测试：

- migration 能创建 `user_profiles`、`profile_items`、`profile_evidence`。
- repository 能保存和查询 profile。
- service 能从历史报告和 feedback 生成 profile evidence。
- 每个 profile item 至少有一条 evidence。
- `not_me` 不进入正向画像。
- `unsure` 不强化画像。
- 无 evidence 时返回 empty profile。
- 用户只能查询自己的 profile。

前端测试 / 验收：

- profile 页面能展示 summary。
- profile 页面能展示 items 和 evidence。
- empty state 清晰说明证据不足。
- 不输出人格诊断。
- 不出现没有 evidence 的高级词。

文档验收：

- 本任务单记录调研与方案确认。
- 实现完成后更新 `07 / 11 / 13 / 12 / 15` 的实际状态。

## 12. AI 生成计划

实现阶段建议顺序：

```text
1. Backend Pydantic schemas：ProfileResponse / ProfileItem / ProfileEvidence。
2. SQLAlchemy models：UserProfileModel / ProfileItemModel / ProfileEvidenceModel。
3. Alembic migration。
4. Repository：memory + database profile repository。
5. Service：profile aggregation / query。
6. API route：GET /api/users/{user_id}/profile。
7. Backend unit / integration tests。
8. Frontend types and profileApi。
9. ProfilePage and navigation entry。
10. Frontend build check。
11. Documentation acceptance update。
```

禁止 AI 自行决定：

- 数据库字段名和状态枚举。
- API path。
- feedback rating 到 evidence direction 的映射。
- 是否引入推荐、RAG、Agent 或 ChromaDB profile。
- 是否把人格、心理、命运判断写入画像。

## 13. 当前结论

```text
V2-B 已完成代码实现、自动验证、PostgreSQL runtime 验收和前端人工验收。
当前实现提供 profile 三表、只读 profile API、后端 profile 聚合、前端轻量画像页和自动化测试覆盖。
```

## 14. 实现记录

2026-06-17 已完成：

```text
Backend:
- 新增 ProfileResponse / ProfileItem / ProfileEvidence schema。
- 新增 UserProfileModel / ProfileItemModel / ProfileEvidenceModel。
- 新增 Alembic migration 20260617_0002_v2b_profiles。
- 新增 memory/database profile repository。
- 新增 profile builder，按 reports + feedback 聚合 profile evidence。
- 新增 ProfileService。
- 新增 GET /api/users/{user_id}/profile。

Frontend:
- 新增 ProfileResponse / ProfileItem / ProfileEvidence types。
- 新增 profileApi。
- 新增 ProfilePage。
- 首页和历史页增加轻量画像入口。

Testing:
- 新增 database profile repository 单元测试。
- 扩展 API flow，覆盖 profile 查询和 feedback evidence。
```

自动验证：

```text
后端：REPOSITORY_BACKEND=memory python -m pytest，16 passed, 3 warnings。
前端：npm run build，通过。
Migration：DATABASE_URL=sqlite+pysqlite:///./v2b_migration_check.db python -m alembic upgrade head，通过。
PostgreSQL migration：python -m alembic upgrade head，通过。
PostgreSQL runtime：database backend 下生成报告 → 提交反馈 → 查询 profile，通过。

PostgreSQL runtime 结果：
- health 200。
- inputs 3 条创建成功。
- analysis job 生成 report 成功。
- report detail 查询成功。
- profile 查询成功。
- feedback 提交成功。
- feedback 后再次查询 profile 成功。
- user_profiles / profile_items / profile_evidence 均有数据写入。
```

人工验收：

```text
2026-06-17 前端手动路径：首页 / 历史页 → 轻量画像页，通过。
验收确认：
- 画像页可显示 profile summary。
- 画像页可显示 profile items。
- 每个条目可显示 evidence refs。
- feedback evidence 可被识别并以用户可读方式展示。
- 页面不输出人格、心理或能力诊断式表达。
- 已修复最初 profile API path 缺少 /api 前缀导致的 404。
- 已优化画像页文案和结构，避免直接暴露 density=low、somewhat_me、feedback_xxx 等内部字段。
```
