# V7-A：Graduation Roadmap & Acceptance Bar

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮定位

V7-A 是 V7 的第一个执行子阶段，但它仍以**产品/工程路线收敛**为核心，不写 runtime 代码。

本轮目标：

```text
把项目从“继续加能力”切换到“明确成型版路线、毕业线和后续版本上限”。
```

V7-A 要回答：

```text
这个项目做到什么程度可以称为作品级完整系统？
V7/V8/V9/V10 各自解决什么，不再无限扩张？
哪些 V6 carry_over 必须做，哪些只适合 V7+ 或 SaaS 化阶段？
每个后续版本的验收证据是什么？
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v7-0-production-validation-graduation-roadmap-research.md`
2. `docs/archive/v6/V6-归档说明.md`
3. `docs/archive/v6/V6-遗留问题.md`
4. `docs/01-产品概念说明书.md` §1 / §3 / §5
5. `docs/02-版本迭代路线图.md`
6. `docs/12-开发任务拆分与里程碑计划.md`
7. `docs/13-验证与评估文档.md`
8. `docs/15-迭代执行记录.md`
9. `docs/20-多模态偏好建模设计文档.md`

## 3. 问题定义

V0-V6 已经把系统推进到：

```text
真实闭环
-> 历史与画像
-> 检索增强与评估
-> 长期 Agent baseline
-> 真实 runtime 与信任边界
-> 多模态 runtime 边界与治理
```

现在的主要风险不再是“缺一个功能”，而是：

```text
版本可能继续发散，导致项目没有清晰成型线。
```

V7-A 的核心任务是把后续路线收束为：

```text
V7：验证体系
V8：产品体验
V9：评估与可观测性
V10：能力沉淀 / Agent 毕业
```

## 4. V7-A 系统边界

本阶段做：

- 定义 V7-V10 的 major version 主题。
- 定义作品级完整系统的 graduation bar。
- 定义生产 SaaS 级能力的明确后置边界。
- 重分类 V6 carry_over：必须、可选、后置、不会做。
- 产出 V7-B/V7-C/V7-D/V7-E 的候选任务入口。
- 更新路线图和执行入口。

本阶段不做：

- 不写后端 runtime 代码。
- 不新增前端页面。
- 不实现真实 audio/video parser。
- 不接入 LangSmith / OTel / Sentry。
- 不直接标记 V6-A real vision validation 为 resolved。
- 不提交 V7-B 之后的实现代码。

## 5. 作品级 Graduation Bar（候选）

作品级完整系统应满足：

```text
用户路径完整：
多模态输入 -> 可解释报告 -> 用户反馈 -> 画像/轨迹更新 -> 历史变化解释 -> 可展示 demo。

工程证据完整：
核心路径自动测试通过、代表样本可复核、runtime 边界可见、治理规则可验证、遗留问题已分类。

表达完整：
README / 展示文档能清楚说明产品价值、系统架构、AI 能力边界和验证方式。
```

明确不是作品级毕业线的必要条件：

- 企业账号体系。
- 多租户计费。
- 大规模监控平台。
- 完整 production OAuth provider。
- 全自动 LLM-as-judge dashboard。
- 完整长视频 / 流媒体下载 / 版权内容处理。

## 6. V7-V10 路线建议

### V7：Production Validation & Graduation Roadmap

目标：

```text
建立真实 runtime smoke、代表样本评估、人工验收 rubric 和毕业路线。
```

用户可感知结果：

```text
系统不只是“能跑”，还知道如何证明自己跑得可信。
```

核心验收：

- V6-A real vision validation 状态被复核。
- 真实 runtime smoke pack 或手动 smoke checklist 已建立。
- golden dataset / representative sample set 已建立。
- manual evaluation rubric 已建立。
- V7-V10 路线已写入路线图。

### V8：Product Experience & Portfolio Demo

目标：

```text
把系统打磨成可展示、可演示、可讲清楚的产品体验。
```

用户可感知结果：

```text
用户可以顺畅完成上传、分析、报告、反馈、画像/轨迹查看的演示路径。
```

核心验收：

- 前端核心路径稳定。
- 报告、profile、timeline、debug 的展示语义清楚。
- 有作品集级 demo script。
- 有截图/录屏/展示文案入口。

### V9：Evaluation / Observability System

目标：

```text
把 V7 的评估包升级为更系统的 quality review / trace / regression 机制。
```

用户可感知结果：

```text
系统质量不只靠人工感觉，而有可复核评估证据。
```

核心验收：

- representative sample set 有版本。
- evidence / governance / usefulness 评估记录可保存。
- Debug trace 和 evaluation summary 对齐。
- 可选引入轻量 LLM-as-judge，但不作为硬门槛。

### V10：Capability / Agent Graduation

目标：

```text
把项目沉淀为长期个性化 AI 的能力样板。
```

用户可感知结果：

```text
系统能解释审美如何变化，并把成熟工作流作为可复用能力讲清楚。
```

核心验收：

- 明确哪些 workflow step 已可沉淀为 skill / capability。
- Agent 行为、观察问题、报告生成、profile 更新具备证据链。
- 最终 archive / portfolio packaging 完成。

## 7. V6 Carry-over 重分类（V7-A 候选）

| 项目 | V7-A 分类 | 目标 |
| --- | --- | --- |
| V6-A 真实 vision 模型人工验收 | V7 必做候选，但允许环境 pending | V7-B |
| 真实 audio ASR / audio feature extraction | V8/V9 决策项，不默认阻塞作品毕业线 | V8+ |
| 真实 video keyframe / subtitle extraction | V8/V9 决策项，不默认阻塞作品毕业线 | V8+ |
| Postgres / Chroma / Ollama smoke 自动化 | V7 必做候选 | V7-B |
| golden dataset / manual eval rubric | V7 必做 | V7-C |
| 产品体验 / demo script | V8 必做 | V8 |
| LangSmith / OTel / Sentry | SaaS 后置或 V9 可选 | V9+ |
| 生产 OAuth provider | SaaS 后置 | V11+ |
| 复杂 LLM-as-judge dashboard | V9 可选，不阻塞作品级毕业 | V9+ |
| enterprise account / billing / scale | SaaS 后置 | V11+ |

## 8. V7-A 产出物

- [x] 更新 `docs/02-版本迭代路线图.md`，补 V7-V10 路线。
- [x] 更新 `docs/12-开发任务拆分与里程碑计划.md`，明确 V7-A 当前执行。
- [x] 更新 `docs/15-迭代执行记录.md`，记录 V7-A route decision。
- [x] 如需要，更新 `docs/README.md` 当前入口。
- [x] 明确 V7-B / V7-C / V7-D / V7-E 子阶段顺序。
- [x] 明确作品级 vs SaaS 级边界。

## 9. 验收标准

- [x] V7-V10 major version 路线清楚且不互相重叠。
- [x] 每个后续 major version 都有一句话目标、用户可感知结果和核心验收。
- [x] V6 carry_over 已重分类，不再作为无边界待办堆积。
- [x] 作品级 graduation bar 明确。
- [x] SaaS 后置能力明确，不阻塞当前项目成型。
- [x] `docs/02`、`docs/12`、`docs/15`、`docs/README.md` 状态一致。
- [x] 本阶段不改 runtime 代码。

## 10. 用户确认（已接受，2026-06-23）

- [x] 接受 V7-A 只做路线收敛和毕业线定义，不写 runtime 代码。
- [x] 接受作品级路线暂定收敛到 V10。
- [x] 接受 V8 聚焦产品体验和作品集 demo。
- [x] 接受 V9 聚焦评估与可观测性系统。
- [x] 接受 V10 聚焦能力沉淀 / Agent 毕业。
- [x] 接受企业 SaaS 能力（账号、计费、多租户、生产监控平台）后置到 V11+，不阻塞作品级毕业。
- [x] 接受真实 audio/video runtime 不默认作为作品级毕业硬门槛。

## 11. AI 生成顺序

确认后建议按以下顺序执行：

1. 更新 `docs/02`，补 V7-V10 路线。
2. 更新 `docs/12`，把当前执行状态切到 V7-A implementation。
3. 更新 `docs/15`，记录 V7-A route decision。
4. 更新 `docs/README.md` 当前入口。
5. 搜索旧状态残留并修正。
6. 视情况提交一版 V7-A 路线文档。

## 12. 当前结论

```text
V7-A 已完成路线收敛实现，状态 ready_for_validation / accepted_auto。
本轮结果：
- `docs/02` 已补 V7-V10 成型路线。
- V7-B/V7-C/V7-D/V7-E 子阶段顺序已明确。
- 作品级 graduation bar 与 SaaS 后置边界已明确。
- V6 carry-over 已重分类，不再作为无边界待办堆积。
- 未改 runtime 代码。
```

## 13. 本轮实现记录（2026-06-23）

- V7 继续作为 Production Validation & Graduation Roadmap。
- V7-A 完成 Graduation Roadmap & Acceptance Bar。
- 后续 major version 收敛为：
  - V8：Product Experience & Portfolio Demo。
  - V9：Evaluation / Observability System。
  - V10：Capability / Agent Graduation。
- 作品级毕业线：
  - 用户路径完整。
  - 工程证据完整。
  - 表达材料完整。
- SaaS 后置能力：
  - 企业账号、计费、多租户。
  - 大规模生产监控平台。
  - 生产 OAuth provider 扩展。
  - on-call / cost governance / production operations。
- 本阶段只改文档，不涉及测试运行。
