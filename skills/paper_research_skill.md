# Agent / AI 顶会论文选题调研 Skill

## 目标

帮助我在 AI / LLM Agent 领域寻找一个有机会发展成顶会论文的研究课题。重点不是泛泛总结论文，而是识别一个可泛化、可复现、可实验验证的失败模式、机制问题、表示问题、评估问题或系统问题。

最终输出必须判断：这个课题是否值得做、是否已经有人做过、创新性是否足够、能否在公开数据集或可构造 benchmark 上验证、适合投哪些会议，以及我当前能力是否能推进。

------

## 一、调研对象

围绕以下方向进行系统调研：

1. LLM Agent 的失败模式
2. 长期个人 Agent / memory agent
3. workflow agent / tool-use agent / software engineering agent
4. 多智能体协作系统
5. agent evaluation / benchmark / trace diagnosis
6. agent 状态管理、回滚、恢复、状态污染
7. agent 个性化、长期适应、用户变化建模
8. agent 在真实工程系统中的可靠性问题

优先关注近三年论文，尤其是 ICLR、NeurIPS、ICML、ACL、EMNLP、COLM、CHI、WWW、KDD、ICSE、FSE、arXiv 高引用或高讨论论文。

------

## 二、调研时必须回答的问题

对每一个候选课题，必须回答以下问题。

### 1. 问题是否真实存在？

检查它是否属于以下至少一种类型：

- 现有方法没有覆盖的新问题；
- 已有问题进入了 agent / 长期交互 / 工具使用 / 真实任务后产生新困难；
- 现有系统反复出现但没有被形式化的工程问题；
- 现有 benchmark 看不到但真实部署中高频出现的问题；
- 现有方法在某些条件下系统性失败；
- 现有表示方式导致问题不可解或难以评估。

如果只是“感觉重要”，但没有论文、系统、benchmark、工程案例或可构造任务支撑，应判定为弱课题。

------

### 2. 是否已有相似工作？

必须检索并比较：

- 是否已有 benchmark；
- 是否已有 failure taxonomy；
- 是否已有 dataset；
- 是否已有方法论文；
- 是否已有 survey 明确总结该问题；
- 是否已有系统已经解决类似问题。

输出时不能只说“有人做过”。必须区分：

- 完全已做，创新空间小；
- 方向已做，但子问题仍有空白；
- benchmark 有了，但机制方法不足；
- 方法有了，但评估场景不真实；
- 工程里存在，但学术上尚未形式化；
- 只在某一领域做过，可以迁移到新场景。

------

### 3. 能否形成顶会级贡献？

从以下贡献类型中判断：

#### A. 问题贡献

提出一个以前没有被清楚定义、但真实重要的 agent 失败模式。

要求：

- 有清晰定义；
- 能构造正负样本；
- 能证明多个现有 agent 都会失败；
- 能说明为什么现有 benchmark 看不到它。

#### B. 表示贡献

提出一种新的表示方式，使 agent 的状态、记忆、任务轨迹、用户变化、工具调用或失败传播变得可建模。

要求：

- 表示不是换名字；
- 能带来可计算、可比较、可诊断或可优化的好处；
- 能接入训练、推理、检索、规划或评估流程。

#### C. 方法贡献

提出新的训练、推理、诊断、恢复、回滚、记忆更新、状态隔离或评估方法。

要求：

- 有明确 baseline；
- 有消融实验；
- 能在多个任务或多个模型上验证；
- 不是简单 prompt engineering。

#### D. Benchmark / Dataset 贡献

构建一个现有 benchmark 覆盖不到的新任务或新评估集。

要求：

- 任务定义清晰；
- 数据来源可信；
- 标注或自动评估可靠；
- 有难度分层；
- 有 baseline 结果；
- 能揭示现有方法的系统性不足。

#### E. 系统贡献

构建一个真正运行的 agent 系统，并证明它解决真实问题。

要求：

- 系统不是简单集成；
- 有新的架构机制；
- 有真实任务或真实用户场景；
- 有端到端实验；
- 有失败分析、成本分析和泛化分析。

------

## 三、候选课题评分表

每个课题按 10 分制评分：

1. 重要性：这个问题是否影响真实 agent 部署？
2. 新颖性：已有工作是否没有充分覆盖？
3. 可形式化程度：能否定义输入、输出、失败条件和评价指标？
4. 可验证性：能否用公开数据、模拟环境或可构造 benchmark 验证？
5. 方法空间：是否不只是发现问题，还能提出解决方法？
6. 泛化性：是否能跨模型、跨任务、跨 agent 框架验证？
7. 顶会匹配度：是否符合 ICLR / NeurIPS / ICML / ACL / EMNLP / CHI / ICSE 等会议兴趣？
8. 工程可行性：以我当前能力和资源，是否能在 2–4 个月内做出初版实验？
9. Baseline 清晰度：是否有可复现的现有方法可比较？
10. 风险：是否容易被审稿人认为只是工程问题、prompt trick、benchmark 小修小补或概念包装？

最后给出总评：

- 8.5–10：强烈值得做，有顶会潜力；
- 7–8.4：可以做，但需要找到更强贡献点；
- 5–6.9：适合作为项目或 workshop，不建议直接冲顶会；
- 5 以下：不建议投入。

------

## 四、输出格式

每次调研一个课题时，按以下格式输出：

### 课题名称

一句话定义这个课题，不要使用空泛大词。

### 核心问题

说明它到底研究什么失败模式、机制问题或表示问题。

### 为什么重要

说明它为什么影响真实 agent 系统，而不是只在概念上好听。

### 已有工作

列出最相关的论文、benchmark、系统和方法，并说明它们做到了什么、没做到什么。

### 创新性判断

明确判断：

- 是否已经有人做过；
- 如果做过，空白在哪里；
- 如果没做过，为什么可能是新问题；
- 审稿人可能会质疑什么。

### 可验证方案

说明可以用什么公开数据集、benchmark、模拟环境、真实 trace 或自建数据验证。

### 可能方法

提出至少三种可行方法路线：

1. 最小可行方法；
2. 中等创新方法；
3. 最有论文潜力的方法。

### 实验设计

包括：

- 任务定义；
- 数据构造；
- baseline；
- 指标；
- 消融实验；
- 泛化实验；
- 错误分析；
- 人工评估是否需要。

### 风险判断

指出这个课题最大的 3–5 个风险，包括：

- 创新性不足；
- benchmark 太小；
- 现有工作太接近；
- 方法只是工程集成；
- 评估不可信；
- 计算资源不足；
- 结果可能不显著。

### 最终结论

必须给出明确判断：

- 值不值得做；
- 是否适合顶会；
- 适合投什么会议；
- 以我当前水平，应该从哪里切入；
- 下一步 7 天应该做什么。

------

## 五、调研时的判断原则

不要迎合我的想法。
如果课题不够新，直接指出。
如果只是概念好听但不可验证，直接否定。
如果已有工作很多，必须说明我还能切哪里。
如果只能做成工程项目而不是论文，也要直接说明。
如果有机会，必须指出最小可行论文路径。

判断一个课题是否值得做时，优先考虑：

1. 是否能揭示现有 agent 的系统性失败；
2. 是否能提出新的问题定义或表示；
3. 是否能构造可靠 benchmark；
4. 是否能提出比 baseline 更稳的方法；
5. 是否能跨模型、跨任务、跨系统验证；
6. 是否能让审稿人相信这是一个领域需要认真对待的问题。

------

## 六、最终目标

不要只是帮我找“有趣方向”。
要帮我找到一个能够发展为论文的研究问题：

- 有问题定义；
- 有相关工作边界；
- 有实验场景；
- 有 baseline；
- 有指标；
- 有方法空间；
- 有审稿人认可的贡献点；
- 有我当前能力可以启动的最小版本。

------

## 七、真实性核验要求

所有论文、benchmark、数据集、代码库、会议接收信息都必须经过核验。

每篇论文必须包含以下字段：

- title
- year
- venue
- authors
- url
- source_type
- verified_status
- verification_note

其中 source_type 只能是：

- arXiv
- OpenReview
- ACL Anthology
- PMLR
- ACM / IEEE / Springer official page
- official project page
- author homepage
- GitHub official repository
- uncertain

verified_status 只能是：

- verified
- uncertain
- remove

判定规则：

1. 如果找不到可靠来源，必须标记为 uncertain。
2. 如果标题、作者、年份、venue 任一关键字段无法核验，不能标记 verified。
3. 如果论文看起来合理但无法找到来源，必须标记 uncertain 或 remove。
4. 不能为了保持方向成立而强行保留论文。
5. arXiv 论文不能随意写成顶会接收论文。
6. under review 不能写成 accepted。
7. withdrawn 论文必须注明 withdrawn。
8. 如果某篇论文是 gap_analysis 的核心论据，必须有可靠来源，否则不能作为核心论据。
9. 如果一个事实只来自模型记忆而没有来源，必须降级为 uncertain。
10. 如果检索结果之间互相矛盾，优先使用官方论文页、会议 proceedings、arXiv/OpenReview/PMLR/ACL Anthology，并在 verification_note 中写明冲突。

------

## 八、Adversarial Review 要求

在判断任何课题是否值得继续前，必须先站在顶会审稿人角度攻击该课题。

必须回答：

1. 这个问题是否已经被已有论文覆盖？
2. 这个课题是否只是已有工作的换名？
3. 这个方法是否只是 prompt / retry / checkpoint / workflow 工程组合？
4. benchmark 是否太小、太人工、太依赖构造？
5. 指标是否只是已有指标改名？
6. baseline 是否足够强？
7. 是否能跨模型、跨任务、跨环境验证？
8. 如果投 ICLR / NeurIPS / ACL / EMNLP，最可能被拒的理由是什么？

输出必须包含：

- strongest rejection reason
- most dangerous related work
- novelty risk
- evaluation risk
- engineering-only risk
- minimum evidence needed to continue

如果无法有效回应核心拒稿理由，应建议暂停或缩小课题。

------

## 九、课题收窄与重命名规则

如果调研发现原始课题过宽、已有工作覆盖过多、术语与已有论文重叠，必须主动提出收窄或重命名。

必须检查：

1. 原始课题名是否与已有论文术语冲突？
2. 原始问题定义是否太宽？
3. 是否需要限定场景？
4. 是否需要限定状态类型？
5. 是否需要限定 benchmark？
6. 是否需要从 general agent 缩小到 software agent / web agent / memory agent？
7. 是否需要从 method paper 改成 benchmark paper？
8. 是否需要从系统贡献改成问题贡献？

输出格式：

- 原始题目
- 风险
- 建议新题目
- 新题目的一句话定义
- 删除哪些过宽内容
- 保留哪些核心内容
- 下一步实验边界

如果 gap_analysis 已经收窄课题，必须同步更新 topic_brief.md。

------

## 十、Research Repo 文件一致性要求

每次完成调研、审计、gap analysis 或实验计划后，必须检查以下文件是否一致：

- topic_brief.md
- paper_table.csv
- related_work.md
- paper_cards/
- gap_analysis.md
- experiment_plan.md
- decision.md

一致性规则：

1. 如果 paper_table 中某论文被标记 uncertain，则 gap_analysis 不能把它作为核心论据。
2. 如果 gap_analysis 收窄课题，topic_brief 必须同步更新。
3. 如果 gap_analysis 认为当前还不能实验，experiment_plan.md 不应强行填写。
4. 如果 experiment_plan.md 已经写出 MVP，decision.md 必须说明当前是否进入 pilot experiment。
5. 如果 related_work 中引用了论文，paper_table 必须有对应条目。
6. 如果某论文 core_read=yes，则必须有对应 paper_card。
7. 如果某论文被标记 remove，related_work 和 gap_analysis 必须删除或降级其论据地位。
8. 如果 venue、year、title 被修正，所有相关文件必须同步修正。
9. 如果 topic_brief、gap_analysis、experiment_plan 对课题名称或范围的描述不一致，必须优先以最新 gap_analysis 为准并同步更新其他文件。
10. 如果 decision.md 给出 Go，但 experiment_plan.md 没有明确数据、baseline、指标和 MVP，则 decision 必须降级为 Narrow 或 Hold。

每次输出最后必须包含：

## File Consistency Check

| File | Status | Required Update |
|------|--------|-----------------|
| topic_brief.md | consistent / outdated | ... |
| paper_table.csv | consistent / needs verification | ... |
| related_work.md | consistent / outdated | ... |
| paper_cards/ | complete / incomplete | ... |
| gap_analysis.md | consistent / risky | ... |
| experiment_plan.md | ready / not ready | ... |
| decision.md | ready / not ready | ... |

------

## 十一、Go / No-Go 决策规则

任何课题进入实验前，必须通过以下检查。

### Go 条件

满足以下条件，才可以进入 experiment_plan 或 pilot experiment：

1. 至少 8 篇核心论文已核验。
2. 至少 5 篇核心论文已有 paper card。
3. gap_analysis 明确指出已有工作覆盖了什么、没有覆盖什么。
4. 最危险的 3 篇 related work 已经被正面比较。
5. 课题已经收窄到一个可实验场景。
6. 有明确 benchmark 或可构造数据。
7. 有 baseline。
8. 有至少 3 个可量化指标。
9. 有最小实验方案。
10. uncertain 论文没有被当作核心论据。

### No-Go 条件

出现以下情况，应暂停或换方向：

1. 核心问题已被已有论文完整覆盖。
2. 只能通过换术语制造新颖性。
3. 没有可复现实验。
4. 没有强 baseline。
5. 方法只是工程拼装。
6. benchmark 完全人工且缺乏真实任务支撑。
7. 指标无法说服审稿人。
8. 主要论据依赖 uncertain 论文。

### 决策输出格式

- Decision: Go / Narrow / Hold / No-Go
- Reason:
- Minimum next step:
- What evidence would change this decision:

说明：

- Go：可以进入最小实验。
- Narrow：方向可做，但必须先收窄。
- Hold：暂缓，先补文献核验或 gap analysis。
- No-Go：不建议继续投入。

------

## 十二、最终使用原则

这个 skill 不只用于生成调研结果，还用于审计调研结果。

使用时必须遵守：

1. 先核验，再判断。
2. 先攻击，再支持。
3. 先收窄，再实验。
4. 先形成 benchmark / baseline / metric，再讨论方法创新。
5. 不把 uncertain 论文当核心证据。
6. 不为了保留课题而降低判断标准。
7. 不把工程集成包装成研究贡献。
8. 每轮调研结束必须给出 File Consistency Check 和 Go / No-Go 判断。