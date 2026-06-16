# V2-0：Memory / User Model 版本级调研与架构拆分

当前状态：

```text
accepted / archived
```

创建日期：

```text
2026-06-16
```

## 1. 本轮定位

V2-0 是 V2 的版本级研究与架构闸门，不是功能实现阶段。

本轮目标：

```text
在继续 V2-B / V2-C 之前，先把 V2 对应的 Agent 前沿方向、记忆系统、轻量用户模型、反馈治理和子阶段拆分设计清楚。
```

为什么补这一轮：

```text
V2-A 已实现历史报告列表与详情回看，但它是历史数据入口，不等于 V2 的 Memory / User Model 设计已经完成。

当前流程暴露出问题：从 V1-E 直接进入 V2-A，跳过了 V2 版本级调研和架构拆分，导致 Agent 前沿方向、记忆写入、记忆更新、记忆遗忘、冲突处理和治理规则没有被系统性研究。
```

## 2. 上游依据

必须引用：

1. `docs/01-产品概念说明书.md`
2. `docs/02-版本迭代路线图.md`
3. `docs/07-数据结构与系统架构文档.md`
4. `docs/11-模块拆分与接口测试文档.md`
5. `docs/12-开发任务拆分与里程碑计划.md`
6. `.cursor/skills/project-development-flow/SKILL.md`
7. `.cursor/skills/project-development-flow/workflow-template.md`

## 3. 对应的 Agent 前沿方向

本轮必须研究并落地到 V2 设计中的方向：

```text
Memory / User Model
Multimodal Preference Modeling
Temporal User Profiling
Preference Explanation
Skill / Capability
Evaluation / Observability
Governance
```

本轮尤其聚焦：

- Memory / User Model
- Temporal User Profiling
- Preference Explanation
- Governance

## 4. 版本核心问题

V2 不只是“历史报告页面”，而是要回答：

```text
系统能不能记住用户过去的输入，并开始描述审美变化？
```

拆成更具体的问题：

```text
什么应该进入轻量记忆？
什么不应该进入轻量记忆？
用户反馈如何影响画像？
被否定的解释如何处理？
新证据和旧画像冲突时怎么办？
画像中的每个倾向如何追溯到输入、报告或反馈？
如何避免把单次分析固化为长期偏好？
用户是否可以查看、修正或删除画像依据？
```

## 5. 本轮调研问题

版本级调研：

- 长期个性化 AI 中 Memory / User Model 通常如何分层？
- 用户偏好画像如何避免过度推断？
- 反馈如何作为正向 / 负向 / 不确定信号进入记忆？
- 记忆系统如何处理遗忘和冲突？
- 个性化记忆如何保持可解释和可治理？

能力级调研：

- 轻量画像最小数据结构应包含什么？
- stable / recent / rejected / uncertain 倾向如何表示？
- feedback weight 是否应该直接修改画像，还是先形成 evidence record？
- 历史报告、feature、interpretation、insight、feedback 的证据链如何连接？
- V2 是否需要单独的 `user_profile` / `profile_items` / `profile_evidence` 表？

实现级调研：

- 当前 PostgreSQL schema 是否足够支撑 V2-B？
- 是否需要 migration？
- 前端是否先展示 profile summary，还是先展示 evidence list？
- 后端 API 应该返回画像快照还是实时聚合？

### 5.1 外部调研记录

#### 记录 1：Generative Agents 的 memory stream / reflection / planning

来源名称：Park et al. 2023 - Generative Agents: Interactive Simulacra of Human Behavior

来源类型：论文 / Agent 记忆架构

链接或出处：`https://arxiv.org/abs/2304.03442`

调研问题：

- Agent 记忆系统如何从原始经历生成更高层的抽象？
- 记忆检索是否只按时间排序？
- V2 是否应该直接做完整 reflection / planning？

核心做法：

- memory stream 记录 agent 的经历。
- 检索结合 recency、relevance、importance。
- reflection 将低层记忆综合成高层洞察。
- planning 使用记忆和 reflection 生成行动计划。

对 V2 的启发：

- 审美系统的 V2 不能只保存历史报告，还需要把历史报告、特征、解释和反馈变成可检索、可解释的 memory evidence。
- 轻量画像不应该直接由单条报告生成，而应从多个 evidence 中聚合。
- V2 可以借鉴 recency / importance / relevance，但不实现完整 agent planning。
- V2-B 的 profile item 应保留 evidence refs，避免变成无来源标签。

不能照搬：

- Generative Agents 面向完整行为模拟，包含 reflection 和 planning；V2 不做主动 Agent 行动。
- importance 不应完全交给 LLM 自行判断，用户反馈应优先于模型推断。

采用结论：

```text
V2 采用“memory evidence → profile item”的轻量路径，不做完整 reflection / planning。
画像倾向必须有 evidence refs；未来 V3/V4 再引入检索和 Agent 行动。
```

#### 记录 2：MemGPT / Letta 的分层记忆

来源名称：MemGPT: Towards LLMs as Operating Systems；Letta Agent Memory

来源类型：论文 / Agent memory system 工程资料

链接或出处：

- `https://arxiv.org/abs/2310.08560`
- `https://www.letta.com/blog/agent-memory/`

调研问题：

- 长期 Agent 记忆是否应该全部塞进 prompt？
- user profile 和原始历史是否应该放在同一层？
- V2 是否需要 memory hierarchy？

核心做法：

- MemGPT 将记忆分为 main context 和 external context。
- core memory 保存用户/persona 等高频、稳定信息。
- archival memory 保存更大规模的长期外部信息。
- LLM 通过工具调用在不同记忆层之间移动信息。

对 V2 的启发：

- V2 应区分“用户画像摘要”和“历史 evidence”。
- `user_profile` / `profile_items` 更接近 core memory 的候选内容。
- 历史报告、输入特征、反馈记录属于 archival / evidence 层。
- V2-B 不应把所有历史报告塞进画像；只把经过规则筛选的倾向写入 profile item。

不能照搬：

- V2 不让 LLM 自主管理记忆。
- V2 不实现 function calling memory manager。
- V2 不把 profile 永久放入 prompt。

采用结论：

```text
V2 采用分层记忆思想：profile summary / profile items 是轻量画像层，report / feature / feedback 是 evidence 层。
```

#### 记录 3：ChatGPT Memory 的用户控制

来源名称：OpenAI - Memory and new controls for ChatGPT

来源类型：产品设计 / 记忆治理资料

链接或出处：`https://openai.com/index/memory-and-new-controls-for-chatgpt/`

调研问题：

- 用户是否应该能查看和删除记忆？
- 系统更新记忆时是否应该透明？
- V2 是否必须实现完整记忆管理 UI？

核心做法：

- 用户可以查看已保存的 memory。
- 用户可以删除单条或全部 memory。
- 用户可以关闭 memory。
- 系统应让用户知道 memory 被更新。

对 V2 的启发：

- V2 的画像不能是黑箱。
- 画像条目至少应该展示来源 evidence。
- V2-B 可以先提供只读 evidence，不一定立刻实现删除 UI。
- V2-E 应把“用户可见、可修正、可删除”的治理能力列为后续验收重点。

不能照搬：

- ChatGPT 是通用对话产品；本项目 V2 只做审美偏好轻量画像。
- V2 不需要完整 settings / memory manager。

采用结论：

```text
V2 画像必须可解释、可追踪；删除/关闭 memory 可以作为 V2-E 或后续增强，但数据结构必须预留治理字段。
```

#### 记录 4：GDPR profiling / erasure / data minimization

来源名称：GDPR Article 17；Data Protection Ombudsman - Automated decision-making and profiling

来源类型：数据治理 / 隐私规范

链接或出处：

- `https://gdpr-info.eu/art-17-gdpr/`
- `https://tietosuoja.fi/en/automated-decision-making-and-profiling`

调研问题：

- 用户画像是否属于 profiling？
- 记忆系统应如何做最小化和删除边界？
- V2 能否让画像产生自动化决策？

核心做法：

- profiling 是用个人数据评估个人方面。
- 数据最小化要求只保存必要数据。
- 用户有权要求删除不再必要或不当处理的数据。
- 自动化决策需要解释、干预和挑战机制。

对 V2 的启发：

- 审美画像虽然不是法律决策，但仍应按 profiling 风险处理。
- V2 不做影响用户权益的自动化决策，只做用户自我理解。
- 画像条目应尽量保存必要字段和 evidence refs，不保存无限原始上下文。
- 被用户否定或撤回的解释不得继续强化。

不能照搬：

- 本项目当前不是上线合规系统，不在 V2 实现完整 GDPR 流程。
- 不引入复杂 consent / account deletion 系统。

采用结论：

```text
V2 采用数据最小化和可撤回原则：只保存轻量画像项、权重、证据引用和状态；不把画像用于自动推荐或决策。
```

#### 记录 5：Temporal User Profiling

来源名称：Considering temporal aspects in recommender systems: a survey；User Modeling and User Profiling survey

来源类型：用户建模 / 推荐系统研究

链接或出处：

- `https://doi.org/10.1007/s11257-022-09335-w`
- `https://arxiv.org/abs/2402.09660`

调研问题：

- 画像是否应该区分长期稳定偏好和短期偏好？
- V2 如何处理近期变化？
- 是否应该把两次报告直接上升为长期结论？

核心做法：

- 用户偏好有长期偏好、短期偏好和演化趋势。
- 时间因素影响用户模型。
- 近期行为不应直接覆盖长期偏好。
- 用户模型可以结合显式反馈和隐式历史。

对 V2 的启发：

- V2-B profile item 应包含 scope：stable / recent / rejected / uncertain。
- V2-D 只能描述“最近两次报告中的变化”，不能说成长期人格变化。
- 反馈权重应随时间和重复证据变化，而不是一次反馈永久决定画像。

不能照搬：

- 推荐系统目标是推荐准确率，本项目目标是解释偏好形成。
- V2 不做点击率、转化率或推荐优化。

采用结论：

```text
V2 画像区分 stable / recent / rejected / uncertain，不把短期输入直接固化为长期偏好。
```

#### 记录 6：Explainable Recommendation 与 explanation feedback

来源名称：ELIXIR；LXR；Explainable Recommendation surveys

来源类型：可解释推荐 / 人类反馈研究

链接或出处：

- `https://arxiv.org/abs/2102.09388`
- `https://doi.org/10.1145/3732292`

调研问题：

- 用户对解释的反馈是否能作为偏好信号？
- 解释是否只要“听起来合理”就够？
- V2 如何避免生成看似合理但与用户偏好不一致的画像？

核心做法：

- 用户可以对解释本身提供反馈。
- explanation feedback 能提供更细粒度的偏好信号。
- 可解释系统要区分 plausible explanation 和 faithful explanation。
- 解释应该反映系统真实依据，而不是事后包装。

对 V2 的启发：

- 用户对 insight 的 rating 可以作为 profile evidence，但不能脱离原 insight 和 report evidence。
- `not_me` / `unsure` / `somewhat_me` / `very_me` 应映射为不同强度和方向的证据信号。
- 画像说明必须展示“为什么系统认为这个倾向存在”。
- 被用户否定的解释不应作为正向画像。

不能照搬：

- V2 不训练推荐模型。
- V2 不做复杂 pairwise explanation learning。

采用结论：

```text
V2 将用户对解释的反馈作为 evidence signal，而不是直接覆盖模型结论；画像必须忠于 evidence。
```

### 5.2 调研总原则

V2 采用以下原则：

```text
1. 先 evidence，后 profile。
2. 先用户反馈，后模型推断。
3. 先轻量画像，后长期 Agent。
4. 先可解释和可撤回，后自动更新。
5. 只描述审美倾向，不做人格诊断。
6. 不把单次输入固化为长期偏好。
7. 不把被否定解释作为正向记忆。
```

## 6. 版本能力地图

V2 能力确认：

```text
V2-0：Memory / User Model 版本级调研与架构拆分
V2-A：历史报告列表与详情回看
V2-B：轻量画像数据模型与 profile evidence
V2-C：反馈权重、否定解释和记忆更新
V2-D：最近两次报告对比与近期变化提示
V2-E：V2 稳定验收与记忆治理检查
```

依赖关系：

```text
V2-A 提供历史报告入口
↓
V2-B 定义什么可以进入轻量画像
↓
V2-C 定义反馈如何改变画像
↓
V2-D 在画像和历史基础上描述变化
↓
V2-E 验收 V2 记忆系统是否可解释、可修正、不过度推断
```

能力分层：

```text
Evidence Layer
- reports
- input_features
- possible_interpretations
- insights
- insight_feedback

Profile Layer
- user_profile
- profile_items
- profile_evidence

Governance Layer
- rejected / uncertain / accepted 状态
- evidence refs
- 用户反馈优先级
- 可查看 / 可修正 / 可删除预留
```

V2 不把 ChromaDB 作为业务记忆来源；ChromaDB 后续只服务 personalized retrieval。

## 7. Memory / User Model 设计闸门

本轮确认以下规则：

```text
记忆对象：
- profile item：一个可解释的审美倾向，例如 low_saturation、person_absent、structured_calm。
- profile evidence：支持或反对该倾向的 report / feature / insight / feedback 引用。
- profile summary：面向用户展示的轻量画像摘要。

什么应该记：
- 多次报告中重复出现的底层特征。
- 用户明确认可的 insight / interpretation。
- 用户明确否定的 insight / interpretation。
- 近期新出现但证据不足的倾向。
- 与画像冲突的新证据。

什么不应该记：
- 单次报告中没有用户反馈支持的高层解释。
- 人格诊断、心理判断、玄学描述。
- 没有 evidence refs 的抽象形容词。
- 被用户明确否定后仍作为正向倾向的解释。
- 与审美无关的敏感个人信息。

记忆写入规则：
- 先写 profile evidence，再聚合 profile item。
- profile item 必须至少有一个 evidence ref。
- stable 倾向需要重复证据或强反馈支持。
- recent 倾向可以由近期报告触发，但不能被描述为长期偏好。
- rejected 倾向只用于避免重复强化，不用于正向画像。

记忆更新规则：
- very_me：强正向 evidence。
- somewhat_me：弱正向 evidence。
- unsure：不确定 evidence，不强化画像。
- not_me：负向 evidence，降低或阻止相关 profile item。
- 模型推断不能覆盖用户反馈。

记忆遗忘规则：
- V2 暂不做自动物理删除。
- V2-C / V2-E 必须预留 status 字段支持 active / rejected / hidden / deleted。
- 被否定的解释从正向画像中移除或降权。
- 过时倾向先标记为 inactive / weakened，不直接删除 evidence。

记忆冲突处理：
- 新证据和旧画像冲突时，不覆盖旧画像。
- 记录 conflict evidence。
- 对用户展示为“近期输入中出现了不同方向”，不写成用户改变人格。

记忆证据来源：
- input_features.feature_json
- aesthetic_reports.report_json
- possible_interpretations.evidence_json
- insights.evidence_json
- insight_feedback.rating / comment

记忆可解释方式：
- 每个 profile item 展示至少一个 evidence ref。
- profile summary 不允许出现没有来源的高级词。
- 用户能看到“系统为什么这样判断”。

用户查看 / 修正 / 删除边界：
- V2-B 至少支持查看画像和 evidence。
- V2-C 支持通过反馈修正画像方向。
- V2-E 评估是否补充隐藏 / 删除 profile item 的 UI 或 API。

防止固化偏见的治理规则：
- 不把画像用于推荐或消费引导。
- 不把画像描述成人格、心理、命运或能力判断。
- 不把一次输入永久化。
- 不把模型判断置于用户反馈之上。
```

### 7.1 V2 数据模型方向

V2-B 应优先考虑新增以下业务表或等价结构：

```text
user_profiles
- id
- user_id
- summary
- version
- created_at
- updated_at

profile_items
- id
- profile_id
- key
- label
- status: stable / recent / rejected / uncertain / inactive
- weight
- confidence
- source_count
- last_seen_at
- created_at
- updated_at

profile_evidence
- id
- profile_item_id
- evidence_type: feature / report / interpretation / insight / feedback
- evidence_id
- direction: positive / negative / uncertain / conflict
- weight_delta
- note
- created_at
```

暂不采用：

- 把画像只塞进 `report_json`。
- 把画像只存在前端。
- 把画像只存在 ChromaDB。
- 不带 evidence 的 profile summary。

## 8. Traceability Matrix

```text
Memory / User Model
↓
轻量画像
↓
V2-B
↓
user_profiles / profile_items / profile_evidence
↓
画像中的每个倾向都有 evidence refs
```

```text
Memory Governance
↓
用户反馈优先和可撤回画像
↓
V2-C / V2-E
↓
profile_items.status / profile_evidence.direction / feedback rating
↓
被否定解释不进入正向画像，用户反馈能修正系统记忆
```

```text
Temporal User Profiling
↓
近期变化提示
↓
V2-D
↓
report comparison / feature trend summary / profile item last_seen_at
↓
只描述“最近两次输入中的变化”，不描述长期人格变化
```

```text
Preference Explanation
↓
画像解释
↓
V2-B / V2-C
↓
profile evidence / insight feedback / report evidence
↓
画像说明必须展示来源，不使用无证据高级词
```

```text
Evaluation / Observability
↓
记忆系统验收
↓
V2-E
↓
profile evidence coverage / rejected explanation recurrence / feedback hit rate
↓
能检查画像是否有证据、是否重复强化被否定解释
```

## 8.1 V2 子阶段最终拆分

```text
V2-0：Memory / User Model 版本级调研与架构拆分
状态：accepted / archived
目标：建立 V2 记忆系统、轻量画像、治理和子阶段拆分的版本级规则。
不做：代码实现、migration、画像 API。
验收：Agent 方向、记忆规则、数据模型方向、traceability matrix 和子阶段拆分完成。
```

```text
V2-A：历史报告列表与详情回看
状态：accepted / archived
目标：提供历史报告入口和详情回看，为 profile evidence 提供上游数据。
说明：该阶段已提前完成，保留为 V2 基础设施。
不做：画像、反馈权重、报告对比。
验收：用户可查看历史报告列表和报告详情。
```

```text
V2-B：轻量画像数据模型与 profile evidence
状态：next / research_required
目标：建立 user_profiles / profile_items / profile_evidence，定义 profile item 和 evidence 的最小闭环。
依赖：V2-0 记忆规则；V2-A 历史报告。
不做：复杂权重、自动遗忘、报告对比、推荐。
验收：能生成只读轻量画像，画像中的每个倾向都有 evidence refs。
```

```text
V2-C：反馈权重、否定解释和记忆更新
状态：planned
目标：让 insight feedback 影响 profile evidence 和 profile item 状态。
依赖：V2-B profile 数据结构。
不做：复杂机器学习、个性化推荐。
验收：very_me / somewhat_me / unsure / not_me 能正确影响画像，not_me 不进入正向画像。
```

```text
V2-D：最近两次报告对比与近期变化提示
状态：planned
目标：基于历史报告和 profile evidence 生成最近变化说明。
依赖：V2-B / V2-C。
不做：长期趋势图、周报 / 月报、人格变化判断。
验收：能描述最近两次输入的共同点和差异，且证据可追踪。
```

```text
V2-E：V2 稳定验收与记忆治理检查
状态：planned
目标：验收 V2 记忆系统是否可解释、可修正、不过度推断。
依赖：V2-B / V2-C / V2-D。
不做：V3 RAG、Agent Runtime、MCP。
验收：profile evidence coverage、被否定解释复现检查、反馈影响检查、治理边界记录。
```

## 9. 本轮不做

- 不写 V2-B 代码。
- 不新增数据库 migration。
- 不实现画像 API。
- 不实现报告对比。
- 不接 RAG。
- 不接 Agent。
- 不接 MCP。
- 不做复杂登录权限。

## 10. Design Promotion

V2-0 是版本级调研与架构闸门。长期有效的设计决策不能只停留在本 iteration 文档中。

2026-06-16 已完成以下设计上升：

```text
数据结构 / 记忆模型 / 存储边界：
已上升到 docs/07-数据结构与系统架构文档.md
- user_profiles
- profile_items
- profile_evidence
- V2 Memory / User Model 写入、更新、冲突、遗忘和治理规则

模块职责 / 输入输出 / 接口测试：
已上升到 docs/11-模块拆分与接口测试文档.md
- 基础用户画像模块职责
- 输入输出契约
- profile item / evidence 模块边界
- V2-B 测试方式和验收标准

验证指标 / 治理检查：
已上升到 docs/13-验证与评估文档.md
- V2 Memory / User Model 数据层、行为层、表达层、治理层验收
- 被否定解释复现检查
- evidence coverage
- 用户反馈优先于模型推断
```

后续 V2-B / V2-C / V2-D / V2-E 必须引用上述权威设计文档中的稳定规则。本文件保留调研过程、外部来源和决策证据。

## 11. 验收标准

本轮完成时必须满足：

- V2 的 Agent 前沿方向映射已明确。
- V2 Memory / User Model 调研已完成。
- 轻量画像、反馈权重、历史对比的依赖关系已明确。
- V2 子阶段重新拆分完成。
- V2-B 开始前必须遵守的版本级规则已写清楚。
- 长期设计决策已上升到权威设计文档。
- `docs/12-开发任务拆分与里程碑计划.md` 和 `docs/15-迭代执行记录.md` 已同步。

验收记录：

```text
2026-06-16：
结果：通过。

已完成：
- V2 Agent 前沿方向映射。
- Memory / User Model 外部调研。
- Temporal User Profiling 外部调研。
- Explainable Recommendation / explanation feedback 外部调研。
- Memory Governance 外部调研。
- V2 能力地图。
- Memory / User Model 设计闸门。
- V2 数据模型方向。
- Traceability Matrix。
- V2 子阶段最终拆分。
- V2-0 长期设计决策已上升到 07 / 11 / 13 权威设计文档。

结论：
V2-0 accepted / archived。
V2-B 可以进入轻量画像数据模型与 profile evidence 的调研阶段，但必须继承已上升到权威设计文档的 V2 Memory / User Model 规则。
```

## 12. 下一步

```text
进入 V2-B：轻量画像数据模型与 profile evidence。

V2-B 只能先做调研和方案确认；不能直接写代码。
```
