# V7-0：Production Validation & Graduation Roadmap 版本级调研与架构拆分

当前状态：

```text
user_confirmed / gate_passed
```

创建日期：

```text
2026-06-23
```

## 1. 本轮定位

V7-0 是 V7 的版本级研究与架构闸门，**不是功能实现阶段**。

本轮目标：

```text
在 V6 Multimodal Runtime & Production Hardening baseline 之上，确定项目从“能力持续扩展”转向“可验证、可演示、可毕业”的后续路线。
```

V7 不应只是继续堆功能，而应回答：

```text
系统距离一个作品级 / 研究型完整系统还差哪些可验证证据？
哪些真实 runtime 必须部署验证？
哪些产品体验必须打磨？
后续最多还需要几个 major version 才能进入成型版？
```

## 2. 上游依据

必须引用：

1. `docs/archive/v6/V6-归档说明.md`
2. `docs/archive/v6/V6-遗留问题.md`
3. `docs/archive/v6/V6-验收核对表.md`
4. `docs/01-产品概念说明书.md` §3
5. `docs/02-版本迭代路线图.md` §14
6. `docs/12-开发任务拆分与里程碑计划.md`
7. `docs/13-验证与评估文档.md`
8. `docs/15-迭代执行记录.md` §39
9. `docs/20-多模态偏好建模设计文档.md`
10. `.cursor/skills/project-development-flow/agent-frontier-design-docs.md`

## 3. 外部调研摘要

本轮外部调研结论：

```text
AI / multimodal / agent 系统从 prototype 走向 production 或作品级完整系统时，关键缺口通常不是“再加一个模型”，而是：

1. golden dataset / representative test set
2. step-level observability / trace
3. runtime smoke test and rollback path
4. modality-specific grounding / validation
5. governance guardrails and manual review loop
6. staged rollout / demo acceptance criteria
```

对本项目的含义：

- V6 已完成默认可信 CI baseline，但真实 runtime smoke 仍是后置项。
- V6 已完成多模态边界，但真实模型部署后的质量与失败模式尚未形成可复现测试包。
- 后续版本需要避免无限扩张，应显式定义“毕业线”。

## 4. 对应的 Agent 前沿方向

V7 主要推进：

```text
Evaluation / Observability：把自动测试、真实 runtime smoke、人工评估样本和 debug trace 组织成可复现验证体系。
Multimodal Preference Modeling：完成 V6-A real vision validation，并决定 audio/video 真实 runtime 是否进入当前成型路线。
Governance：把 V6 的边界测试升级成 release / demo 前的验收门。
Skill / Capability：为后续能力沉淀准备可复用评估包，而不是立即做复杂 skill platform。
```

V7 继承并不得破坏：

```text
Memory / User Model：未经 feedback 的 feature-only evidence 不得稳定写入 profile。
V5 Trust Boundary：user scope、runtime visibility、external confirm flow。
V6 Multimodal Boundary：metadata-only / placeholder 不得伪装成真实内容理解。
```

## 5. V6 遗留问题重分类（进入 V7 前）

来源：`docs/archive/v6/V6-遗留问题.md`

| V6 legacy item | V7 分类 | 目标子阶段 / 说明 |
| --- | --- | --- |
| V6-A 真实 vision 模型人工验收 | **V7 必做候选** | 作为 real runtime validation gate；若用户仍无模型，可保留 pending_validation |
| 真实 audio ASR / audio feature extraction | **V7/V8 决策项** | 不应默认硬做；需先判断是否对作品毕业线必要 |
| 真实 video keyframe / subtitle / remote video extraction | **V7/V8 决策项** | 与 audio 一样先判断价值/成本 |
| Postgres / Chroma / Ollama smoke 自动化进入 CI | **V7 必做候选** | 不一定进入默认 CI，但至少形成可运行 smoke command |
| 生产级 LangSmith / OpenTelemetry / Sentry | **V7 可选/后置** | 作品级可先保持 debug trace；生产级 SaaS 才强制 |
| 生产级 OAuth provider（非 mock_oauth） | **V8+ / 可选** | 当前不是成型版核心风险 |
| 复杂 evaluation dashboard / LLM-as-judge | **V8+ / 可选** | V7 先做 small golden set 和 deterministic checks |
| failure replay 一键重跑 workflow | **V7+ / 可选** | 只有真实 runtime smoke 频繁失败时再做 |

## 6. V7 版本主题候选

### 候选 A：Real Runtime Validation

```text
聚焦真实 vision / Ollama / Postgres / Chroma smoke，补部署验证证据。
```

优点：承接 V6 pending_validation，工程风险明确。

风险：如果用户暂时没有模型，版本会被外部环境阻塞。

### 候选 B：Product Demo Graduation

```text
聚焦前端体验、演示路径、作品集表达和毕业验收。
```

优点：更接近作品完成。

风险：真实 runtime 和评估证据不足时，容易变成漂亮 demo。

### 候选 C：Production Validation & Graduation Roadmap（推荐）

```text
把 V7 定义为“验证体系 + 毕业路线”版本：
- 不强制一次性补完所有真实模态模型。
- 先把真实 runtime smoke、golden dataset、人工评估、版本毕业线建起来。
- 同时明确 V8/V9/V10 最多做什么，避免无限滚版本。
```

推荐理由：

```text
它既承接 V6 的 pending_validation，又回答用户关心的“还有多少个 V”。
它把后续路线收敛到 V10 左右，而不是继续开放式扩展。
```

## 7. V7 能力地图（候选）

```text
V6 baseline（已归档）
├── multimodal runtime adapter boundary
├── mock / metadata-only / disabled / ollama_vision
├── runtime debug boundary
├── profile governance
└── default pytest baseline 151 passed

V7 目标增量（候选）
├── V7-A Graduation Roadmap & Acceptance Bar
│   ├── 明确 V7/V8/V9/V10 的主题和毕业线
│   ├── 明确作品级 vs SaaS 级边界
│   └── 明确哪些 carry_over 不再阻塞成型版
├── V7-B Real Runtime Smoke Pack
│   ├── Ollama report / vision smoke commands
│   ├── Postgres / Chroma smoke checklist
│   └── optional smoke 不污染默认 CI
├── V7-C Golden Dataset & Evaluation Pack
│   ├── 小型代表性样本集
│   ├── evidence / governance / usefulness rubric
│   └── manual review record template
├── V7-D Product Demo Acceptance
│   ├── 核心用户路径复核
│   ├── 展示/作品集 demo 条件
│   └── debug / report / profile 可解释性检查
└── V7-E Validation Governance & Closure
    ├── 横切验证
    ├── legacy issue audit
    └── V8/V9/V10 路线复核
```

## 8. 建议的后续 major version 上限

建议把“作品级 / 研究型完整系统”的路线收敛到：

```text
V7：Production Validation & Graduation Roadmap
V8：Product Experience & Portfolio Demo
V9：Evaluation / Observability System
V10：Capability / Agent Graduation
```

不建议无限追加 major version。

V10 的毕业线建议定义为：

```text
用户可以完成一条清晰路径：
多模态输入 -> 可解释报告 -> 反馈 -> 画像/轨迹更新 -> 历史变化解释 -> 可展示 demo。

开发者可以证明：
核心路径有自动测试、代表样本评估、debug trace、治理边界和已分类遗留问题。
```

如果目标提升为生产 SaaS，则另设：

```text
V11+：Production SaaS / Operations / Account / Billing / Scale
```

但这不应作为当前作品级毕业线的必要条件。

## 9. 关键架构决策（待确认）

### 9.1 V7 是否强制真实模型部署？

推荐：

```text
不强制。
```

理由：

- V6-A real vision validation 可作为 V7-A/V7-B 的优先任务，但如果用户仍未部署模型，不应阻塞 V7 其他验证体系建设。
- V7 应建立 smoke pack 和人工验收模板，让模型部署后能快速补验证。

### 9.2 V7 是否实现真实 audio/video runtime？

推荐：

```text
V7-0 先决策，不默认实现。
```

判断标准：

- 是否有可部署模型。
- 是否有代表样本。
- 是否对作品级 demo 必要。
- 是否会显著增加治理风险。

### 9.3 V7 是否接入 LangSmith / OTel / Sentry？

推荐：

```text
作品级优先保留当前 debug trace + smoke/eval records。
生产 SaaS 才强制接入外部观测平台。
```

### 9.4 V7 是否启动前端体验打磨？

推荐：

```text
V7 先定义 demo acceptance bar；大规模前端体验打磨放 V8。
```

## 10. V7 验收标准（版本级候选）

- [ ] V7 明确项目成型版路线，建议收敛到 V10 左右。
- [ ] V7 明确作品级与生产 SaaS 级边界。
- [ ] V7 产出真实 runtime smoke pack 或手动 smoke checklist。
- [ ] V7 产出小型 golden dataset / representative sample set。
- [ ] V7 产出 manual evaluation rubric。
- [ ] V7 复核 V6-A real vision validation 的状态。
- [ ] V7 不把没有部署的真实模型伪装成已验证能力。
- [ ] V7 不强制真实 audio/video runtime，除非用户明确具备模型和样本。
- [ ] V7 后续子阶段都有明确 acceptance criteria。

## 11. 明确不做

V7-0 不做：

- 不写 runtime 代码。
- 不创建真实 audio/video parser。
- 不接入生产 SaaS 账号、计费、团队空间。
- 不做复杂 LLM-as-judge dashboard。
- 不把 V7 直接变成 V8/V9/V10 的混合实现。
- 不把 V6 pending_validation 直接标记为 resolved。

## 12. 建议子阶段拆分（待确认）

```text
V7-A Graduation Roadmap & Acceptance Bar
V7-B Real Runtime Smoke Pack
V7-C Golden Dataset & Evaluation Pack
V7-D Product Demo Acceptance Planning
V7-E Validation Governance & Closure
```

执行顺序：

```text
先确定毕业线
-> 再补真实 runtime smoke
-> 再补代表样本评估
-> 再定义产品 demo 验收
-> 最后做横切治理和 closure
```

## 13. 对权威文档的影响

V7-0 暂不直接修改 runtime 设计。

可能需要在 V7-A 后更新：

- `docs/02-版本迭代路线图.md`：补 V7-V10 成型版路线。
- `docs/13-验证与评估文档.md`：补 golden dataset / manual evaluation rubric。
- `docs/20-多模态偏好建模设计文档.md`：如真实 audio/video runtime 被纳入 V7/V8，再扩展解析状态。
- `.cursor/skills/project-development-flow/agent-frontier-design-docs.md`：如 V7 决定创建 Evaluation / Observability 独立领域文档，再更新登记表。

## 14. 用户确认（已接受，2026-06-23）

- [x] 接受 V7 主题为 **Production Validation & Graduation Roadmap**。
- [x] 接受 V7 不是继续堆功能，而是建立真实 runtime smoke、评估包、毕业线。
- [x] 接受作品级路线建议收敛为 V7-V10。
- [x] 接受 V7 不强制真实 audio/video runtime，除非用户已具备模型与样本。
- [x] 接受 V6-A real vision validation 进入 V7 优先验证项，但仍可在无模型时保留 pending。
- [x] 接受 V7-A 先定义 graduation roadmap 与 acceptance bar，再进入实现子阶段。

## 15. 当前结论

```text
V7-0 版本级调研已确认，状态 user_confirmed / gate_passed。
下一步进入 V7-A Graduation Roadmap & Acceptance Bar。
```
