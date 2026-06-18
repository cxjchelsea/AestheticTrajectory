# V4-B：Aesthetic Trajectory & Temporal Profiling

当前状态：

```text
implementation_completed / pending_validation
```

创建日期：

```text
2026-06-18
```

## 1. 本轮目标

在 V4-A runtime 地基与 V2/V3 记忆基线之上，建立 **审美时间轴与 temporal profiling**：

```text
报告 / 对比 / 反馈 等业务事实
↓
生成可追溯 timeline events（持久化）
↓
时间轴 API + 前端页面（按时间浏览）
↓
周期性摘要（周/月，聚合已有 evidence，非 LLM 自由发挥）
↓
主题复现 / 特征迁移提示（带 evidenceRefs）
↓
profile temporal states 扩展（含 weakening）
```

本轮完成后，用户应能：

- 在时间轴页按时间查看「新解释出现」「特征迁移」「稳定偏好复现」「解释被否定」等事件。
- 展开每条事件查看关联 `reportId` / `insightId` / `feedbackId` / `comparison` evidence。
- 查看基于已有事件的周/月观察摘要（明确标注为聚合说明，非诊断）。
- 在 profile 中看到 `weakening` 等与时间相关的状态（继承 V2 stable/recent/rejected 语义）。

## 2. 上游版本决策

引用 `docs/iterations/v4-0-long-term-personalized-agent-research.md` §6.1、§7.3、§V4-B：

- V4-B 在 V4-A 之后、V4-C 之前；**不**依赖 Agent、MCP、知识图谱 runtime。
- 时间轴条目必须链接 report / insight / feedback / comparison evidence。
- 周期性摘要只能聚合已有 evidence，**不能**生成无来源的新偏好。
- 不得把轨迹写成心理/人格/人生阶段叙事（继承 V2-D comparison 治理）。
- profile 正向证据仍只来自 feedback + feature evidence；timeline **不**绕过 feedback 直接改 profile。

引用 `docs/19-记忆与用户模型设计文档.md` §10.1：

- L5「跨报告变化与时间轴」从 comparison 只读升级为 **持久化 timeline + 周期摘要视图**。
- Agent 化之前，timeline 由确定性规则生成，不用黑盒 LLM 摘要替代 evidence。

引用 `docs/07-数据结构与系统架构文档.md` §5.14：

- 采用已占位的 `aesthetic_timeline_events` 表；本迭代确认最终字段与 event_type 枚举。

## 3. 本轮解决什么问题

本轮解决：

```text
如何让「最近两次对比」（V2-D）扩展为跨多报告、可回溯、可治理的审美轨迹，同时不引入 Agent 或无证据叙事？
```

本轮不解决：

- Agent 观察摘要 / 主动提问（V4-D）。
- 知识图谱与外部 RAG runtime（V4-C）。
- 真实 LLM 生成周期摘要（V4-B 用规则模板 + evidence 聚合）。
- 复杂时间衰减 ML 模型、趋势预测、推荐导向。
- 自动修改 profile 权重（仍只经 feedback governance）。
- 推送订阅、邮件周报、后台定时任务（V4-B 仅 on-demand API）。

## 4. 当前实现快照（V4-B 起点）

| 能力 | 当前状态 |
| --- | --- |
| 最近两次对比 | `GET /api/users/{id}/reports/comparison/latest` + `ReportComparisonPage`（V2-D） |
| 历史报告列表 | V2-A 已实现 |
| Profile temporal status | `stable` / `recent` / `rejected` / `uncertain` / `inactive` 等；**无** `weakening` |
| `aesthetic_timeline_events` | `07` §5.14 占位；**无** migration / model / API |
| workflow `updateTrajectory` | v4-0 候选 step；**未**实现 |
| 前端路由 | 无 `timeline` 路由 |

## 5. 外部调研与方案选择

调研层级：

```text
版本级：引用 v4-0 §6.1（Explainable Temporal User Profiling）
能力级：timeline event model、周期摘要、profile weakening
实现级：写入时机、API、前端信息架构、测试策略
```

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| 时间轴数据从哪来？ | **混合**：报告完成 / 对比可用 / 关键 feedback 时 **写入** `aesthetic_timeline_events`；查询时按时间排序，不每次全量重算 |
| 周期摘要谁生成？ | **规则聚合**（非 LLM）：统计期内 events + report refs，模板句 + evidence 列表 |
| 与 comparison 关系？ | comparison 结果可 **派生** `feature_shift` / `interpretation_decline` 事件；保留 V2-D API 不变 |
| profile weakening？ | 当 timeline 出现 `interpretation_decline` 或 repeated `not_me` 且 feature 计数下降时，标记相关 profile item 为 `weakening`（只读展示，不改 weight 算法主路径） |
| LLM 摘要？ | V4-B **拒绝**；V4-D Agent 才可考虑 evidence-bound 摘要 |
| 写入失败？ | timeline 写入失败 → 记录 debug/fallback；**不**阻塞 report 完成（非核心增强，按治理规则） |

### 5.2 外部调研记录

#### 记录 1：Explainable Temporal User Profiling（短长期分离）

来源名称：Towards Explainable Temporal User Profiling with LLMs (TETUP)

来源类型：论文

链接或出处：

- `https://arxiv.org/pdf/2505.00886`
- `https://github.com/milsab/TETUP`

调研问题：

- 为何静态 profile 不够？
- 短长期分离如何支持可解释性？

核心做法：

- 区分 recent behaviors 与 persistent tendencies。
- 文本摘要 + attention 融合短长期表示；摘要本身可作为解释依据暴露给用户。

对 V4-B 的启发：

- 产品层需要 **时间语义分离**（recent vs stable），但 V4-B 用 **确定性事件 + 已有 report/profile 事实** 实现，不用 LLM 生成 profile 文本。
- 周期摘要应标明「基于哪些报告/事件」，对应论文中的 explainability 诉求。

采用结论：

```text
V4-B 采用事件时间轴 + 规则周期摘要；语义上区分 recent/stable/weakening，实现上不引入 LLM 自由摘要。
```

#### 记录 2：时间型推荐中的节奏与变化（feature shift）

来源名称：TME-PSR: Time-aware, Multi-interest, and Explanation Personalization

来源类型：论文

链接或出处：`https://arxiv.org/html/2604.09439v1`

调研问题：

- 用户兴趣「节奏」与突然变化如何建模？

核心做法：

- 长短期时间节奏分别编码；解释任务与推荐任务可分离考虑时间偏好。

对 V4-B 的启发：

- 审美轨迹需要识别 **突然的风格迁移**（gap 后特征集变化）与 **稳定复现**（同 feature 跨多 report）。
- V4-B 用 `feature_shift` / `stable_preference` event_type + evidence_refs 表达，不做 embedding 级节奏模型。

采用结论：

```text
用离散 timeline events 表达 shift/stable，不做连续时间衰减模型。
```

#### 记录 3：V2-D 最近对比作为轨迹种子

来源名称：项目已实现 `report_comparison.py`

来源类型：项目代码 / V2-D 验收

链接或出处：

- `backend/app/services/report_comparison.py`
- `docs/iterations/v2-d-report-comparison.md`

调研问题：

- 现有 comparison 能否复用为 timeline 事件来源？

核心做法：

- 对比 `lowLevelFeatures` / `possibleInterpretations` / `insights` 生成 `featureChanges` / `interpretationChanges`，每条带 `evidenceRefs`。

对 V4-B 的启发：

- 每次成功生成 comparison 时，可追加 0..n 条 timeline events，避免重复实现对比逻辑。
- timeline UI 可链接到已有 comparison 视图。

采用结论：

```text
comparison 作为 timeline 派生源之一；V2-D API 保持兼容。
```

### 5.3 方案对比

#### 时间轴存储

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 纯 on-read 派生 | 无 migration | 性能差、难审计、无法附 user note | 拒绝 |
| B 仅 append events 表 | 可追溯、可治理、与 07 一致 | 需 migration + 写入钩子 | **采用** |
| C 额外 observation_summaries 表 | 摘要独立版本化 | 超 V4-B 范围 | 推迟到 V4-D |

#### 周期摘要

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A LLM 生成周报 | 文案自然 | 无证据风险、超范围 | 拒绝 |
| B 规则模板 + event 统计 | 可测试、evidence-bound | 文案较机械 | **采用** |
| C 仅前端聚合 | 实现快 | 无双端契约、难测 | 拒绝 |

## 6. 系统边界

### 6.1 必做

- [ ] Alembic migration：`aesthetic_timeline_events`（对齐 07 §5.14，补充 `source_refs_json` 等必要字段）。
- [ ] `TimelineEvent` Pydantic schema + repository（memory + database）。
- [ ] `timeline_builder`：从 report / comparison / feedback 生成 events。
- [ ] workflow 或 report 保存后钩子：写入 timeline events（best-effort + debug）。
- [ ] `GET /api/users/{user_id}/timeline`（分页、时间过滤）。
- [ ] `GET /api/users/{user_id}/timeline/summary`（`period=week|month`）。
- [ ] 前端时间轴页 + 从 history/profile 入口导航。
- [ ] `ProfileItemStatus` 增加 `weakening`（schema + builder 最小规则 + 治理测试）。
- [ ] 单元测试 + 集成测试 + governance 扩展。
- [ ] 上升 `07` / `11` / `19` §10.1；`15` 执行记录。

### 6.2 不做

- [ ] Agent 观察摘要、对话壳。
- [ ] LLM 生成周期文案。
- [ ] 知识图谱、MCP、Chroma 检索历史。
- [ ] 趋势图 / 可视化图表库（V4-B 用列表 + 时间分组即可）。
- [ ] 用户编辑 timeline 事件（只读系统生成）。

## 7. 架构影响

### 7.1 数据模型（拟采用）

在 `07` §5.14 基础上细化：

```text
aesthetic_timeline_events
  id (uuid)
  user_id
  event_type          # enum，见下
  title               # 短标题，模板生成
  description         # 可选补充说明
  related_report_ids  # json array
  related_insight_ids # json array（可空）
  related_feedback_ids# json array（可空）
  evidence_json       # { evidenceRefs, comparisonRef?, featureKeys?, notes? }
  occurred_at         # 业务时间（通常 = report.created_at 或 feedback.created_at）
  created_at
```

`event_type`（首版）：

```text
new_interpretation      # 新解释/洞察方向首次出现
interpretation_decline  # 解释减弱或被 not_me 否定
feature_shift           # 底层特征分布变化（来自 comparison）
style_shift             # 跨报告主题/特征组合迁移（规则检测）
contradiction_detected  # 与历史 stable 偏好冲突的信号（只作提示）
stable_preference       # 跨 ≥3 报告重复出现的 feature/interpretation
report_completed        # 锚点事件：一次分析完成（可选，便于稀疏历史）
```

### 7.2 API 设计（拟）

| 路径 | 方法 | 说明 |
| --- | --- | --- |
| `/api/users/{user_id}/timeline` | GET | `limit`、`cursor`/`offset`、`from`、`to` |
| `/api/users/{user_id}/timeline/summary` | GET | `period=week\|month`；返回 `summaryText`、`eventCount`、`highlights[]`、`disclaimer` |
| `/api/users/{user_id}/timeline/events/{event_id}` | GET | 单条详情（可选，首版可合并到 list） |

响应原则：

- 每条 event 带 `evidenceRefs` 或可展开的 `sourceRefs`。
- `disclaimer` 固定包含「非人格/心理诊断」类治理文案（继承 V2-D）。
- 历史不足时返回明确 `message` 空状态。

### 7.3 模块与目录（拟）

```text
backend/app/schemas/timeline.py
backend/app/models/persistence.py          # TimelineEventModel
backend/app/repositories/timeline_repository.py
backend/app/services/timeline_builder.py
backend/app/services/timeline_summary.py
backend/app/api/routes/timeline.py
backend/app/workflows/steps/update_trajectory.py   # 或 hook 于 save_report
frontend/src/pages/TimelinePage.tsx
frontend/src/services/timelineApi.ts
frontend/src/types/aesthetic.ts            # TimelineEvent types
```

### 7.4 workflow 集成

```text
... → generate_report → compute_report_evaluation → save_report_and_trace
  → update_trajectory（新增）
      - 读取本 job report + 最近 comparison + 本 job feedback
      - timeline_builder.build_events(...)
      - repository.append_events（idempotent：同 report_id + event_type + key 不重复插入）
```

降级：

- timeline 写入失败 → `fallback_events` + `boundaryWarnings`；report 仍 completed。

### 7.5 前端

- 新增路由 `timeline`；Home / History / Profile 提供入口。
- 列表按日期分组；点击展开 evidence 与 report 链接。
- 周期摘要区块：周/月切换；显示「基于 N 次分析、M 条变化事件」。
- **不做** 复杂图表；与现有页面风格一致。

### 7.6 Profile weakening（最小规则）

在 `profile_builder` 或独立 `temporal_profile_hints` 只读层：

- 若某 profile item 的 key 在最近 timeline `interpretation_decline` 中出现 ≥1 次 → 状态可标 `weakening`。
- `weakening` **不**进入 stable/recent 正向摘要句。
- 权重计算逻辑不变或仅只读展示 override；避免 silent 改 profile。

## 8. 验收标准

### 8.1 自动测试

- memory backend 全量 pytest 仍通过。
- `timeline_builder`：给定 fixture reports/comparison/feedback → 期望 events。
- API：空历史、单报告、多报告、分页。
- governance：timeline summary 不含「人格」「心理」「能力」禁用词；events 均有 evidence。
- profile：`weakening` 状态与 governance 测试扩展。

### 8.2 人工验收清单（§10.3）

- [ ] 完成 ≥3 次分析后，时间轴出现按时间排序的 events。
- [ ] 点击事件可追溯到具体 report / insight / feedback。
- [ ] 周/月摘要仅引用期内 events/reports，不声称新偏好。
- [ ] `not_me` 反馈后可见 `interpretation_decline` 或等价事件。
- [ ] comparison 页与时间轴内容一致、不矛盾。
- [ ] profile 页对 weakening 项有可读说明（非诊断）。
- [ ] V3-E governance 测试仍全部通过。

## 9. AI 生成代码顺序（确认后执行）

1. Schema + Alembic migration + repository
2. `timeline_builder` + unit tests
3. workflow hook / `update_trajectory` step
4. timeline API routes + integration tests
5. `timeline_summary` service
6. Frontend types + API client + TimelinePage
7. Profile `weakening` + governance tests
8. 上升 `07` / `11` / `19` + `15` 记录

## 10. 权威设计文档更新判断

实现开始前更新：

- `docs/07` §5.14 字段定稿
- `docs/11` 新增 timeline / temporal summary 模块契约
- `docs/19` §10.1 从占位改为「V4-B 实现中」映射

实现结束后更新：

- `docs/13` 若新增 governance 检查项
- `agent-frontier-design-docs.md` §3.3 → `partial`（以 `19` §10.1 为入口，暂不强制 `docs/21`）

## 11. 用户确认（已接受）

- [x] 接受 **持久化 `aesthetic_timeline_events` 表** + workflow 写入钩子。
- [x] 接受周期摘要为 **规则模板聚合**，V4-B 不使用 LLM 生成。
- [x] 接受首版 event_type 枚举（§7.1）与 **列表式** 时间轴 UI（无图表）。
- [x] 接受 `weakening` 为 **只读 temporal 状态**，不自动改 profile 权重。
- [x] 接受 timeline 写入失败 **不阻塞** report 完成（显性降级）。

## 12. 当前结论

```text
V4-B 实现已完成，状态 implementation_completed / pending_validation。
已实现：timeline events 持久化、update_trajectory workflow、timeline/summary API、TimelinePage、weakening 展示。
memory backend pytest：71 passed（2026-06-18）。
待完成：人工验收 §8.2、上升 07/11/19、15 记录。
```
