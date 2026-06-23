# V6-0：Multimodal Runtime & Production Hardening 版本级调研与架构拆分

当前状态：

```text
user_confirmed / gate_passed
```

创建日期：

```text
2026-06-23
```

## 1. 本轮定位

V6-0 是 V6 的版本级研究与架构闸门，**不是功能实现阶段**。

本轮目标：

```text
在 V5 Production Runtime & Trust Boundary baseline 之上，明确 V6「真实多模态内容解析 + 生产集成硬化」的能力地图、边界、子阶段拆分与验收标准。
```

为什么必须先做这一轮：

```text
V5 已完成真实 report LLM、identity、external source OAuth 边界和 resilience/debug。
但输入层仍存在明显断点：image 只上传不解析，music/video 仍 metadata-only，external source 仍 mock_oauth，CI/database fixture 仍偏本机。

如果直接把 vision / ASR / video caption 塞进现有 workflow，容易破坏 V1-V5 的 evidence-first、schema validation、profile governance 与 fail-fast 边界。
V6-0 的职责是先回答：哪些模态先解析、解析结果如何进入 InputFeature、如何标记真实/占位、如何验证不伪造证据，以及生产 hardening 哪些是 V6 必做。
```

## 2. 上游依据

必须引用：

1. `docs/archive/v5/V5-遗留问题.md` §5
2. `docs/archive/v5/V5-归档说明.md`
3. `docs/01-产品概念说明书.md` §3.2 / §3.6 / §3.7
4. `docs/20-多模态偏好建模设计文档.md`
5. `.cursor/skills/project-development-flow/agent-frontier-design-docs.md`
6. `docs/02-版本迭代路线图.md` §12-§14
7. `docs/12-开发任务拆分与里程碑计划.md`
8. `docs/13-验证与评估文档.md`
9. `docs/15-迭代执行记录.md` §32

## 3. 对应的 Agent 前沿方向

V6 主要推进：

```text
Multimodal Preference Modeling：真实 image / audio / video 内容解析进入统一特征层。
Evaluation / Observability：真实多模态解析需要更严格的 trace、fixture、CI hardening。
Governance：防止模型把不确定视觉/音频解释写成稳定偏好或人格判断。
Skill / Capability：为后续“图片审美分析能力 / 音视频审美片段分析能力”沉淀边界。
```

V6 继承并不得破坏：

```text
Memory / User Model：profile positive evidence 仍只来自可追溯、可解释、可反馈证据。
V5 Trust Boundary：identity scope、real/mock runtime visibility、external confirm flow。
V3/V4 Retrieval & Agent：RAG / Agent / external context 仍是解释辅助，不是偏好事实。
```

## 4. 版本核心问题

V6 要回答：

```text
系统能否从“登记多模态输入”升级为“真实理解多模态内容”，并且在生产集成、测试和治理边界上仍可信？
```

拆成更具体的问题：

```text
图片内容解析应先做本地/远程 vision caption，还是直接抽结构化 InputFeature？
音乐内容解析先做 metadata 增强、歌词/备注，还是 ASR / audio embedding？
视频内容解析先做关键帧 caption、标题/字幕，还是完整视频理解？
真实多模态解析失败时哪些 fail-fast，哪些可以 degrade？
解析输出如何标记 promptVersion/modelName/source modality，避免与 mock/heuristic 混淆？
CI 如何覆盖真实 runtime 边界而不依赖外部模型服务？
是否在 V6 引入 testcontainers / 干净 DB fixture，还是继续 memory + smoke？
是否接入生产级 OTel/LangSmith，还是保持 dev-only boundary？
```

## 5. V5 遗留问题重分类（进入 V6 前）

来源：`docs/archive/v5/V5-遗留问题.md` §5

| 原 carry_over | V6 分类 | 目标子阶段 / 说明 |
| --- | --- | --- |
| 音乐、视频真实内容解析 | **V6 必做候选** | V6-B 或 V6-C；先定义边界，不一次性全量视频理解 |
| 真实 vision 内容分析 | **V6 必做候选** | V6-A；优先 image caption / structured visual feature |
| 生产级 OAuth provider（非 mock_oauth） | **V6 可选/后置** | V6-D；不应阻塞多模态主线 |
| integration test 干净 DB / testcontainers | **V6 hardening 候选** | V6-D；Windows/Docker 成本需评估 |
| Pydantic / FastAPI alias warnings 清理 | **V6 tech-debt** | V6-D；若升级 FastAPI/Pydantic 则一并处理 |
| 生产级 LangSmith / OpenTelemetry pipeline | **V6 可选** | V6-D；真实多模态 trace 的加分项 |
| 复杂 evaluation dashboard / LLM-as-judge | **V6+ / 非主线** | 不作为 V6 必做，避免偏离解析与证据治理 |
| failure replay 一键重跑 workflow | **V6+** | 仅在真实多模态失败回放需要时评估 |
| cross-user / 长期 grouping stability 平台 | **V6+** | 当前不是多模态解析首要风险 |

## 6. 能力地图（候选）

```text
V5 baseline（已归档）
├── anonymous session + object-level scope
├── Ollama report LLM
├── mock_oauth external source confirm flow
├── Chroma/knowledge graceful degrade
└── V5 governance validation

V6 目标增量
├── V6-A Image Understanding Runtime
│   ├── image caption / visual feature extraction
│   ├── image evidence refs
│   └── mock vs real vision boundary
├── V6-B Audio / Music Understanding Boundary
│   ├── metadata + optional lyric/transcript path
│   ├── ASR/audio feature spike decision
│   └── music remains truthful if content unavailable
├── V6-C Video Understanding Boundary
│   ├── keyframe / subtitle / metadata strategy
│   ├── cost and latency guardrails
│   └── video evidence trace
├── V6-D Production Hardening
│   ├── DB fixture / testcontainers decision
│   ├── Pydantic/FastAPI alias warning cleanup
│   ├── optional OTel/LangSmith boundary
│   └── runtime config hardening
└── V6-E Multimodal Governance Validation & Closure Prep
    ├── cross-modal evidence governance
    ├── no diagnostic output
    └── archive preparation
```

## 7. 子阶段拆分（候选，待 §12 确认）

### V6-A：Image Understanding Runtime

目标：

```text
让 image 输入从“上传后 metadata/placeholder”升级为可追溯的视觉内容解析，产出结构化 InputFeature，并在 debug 中明确 model/prompt/runtime 边界。
```

必做：

- 更新 `docs/20` 中 image 解析语义。
- 引入 `ImageFeatureExtractor` 或等价 adapter。
- 图片文件读取与 payload 构建。
- 输出 `InputFeature`，保留 evidence / promptVersion / modelName。
- 失败语义：真实 vision runtime 失败是否 fail-fast 需在 V6-A 任务单定稿。

不做：

- 复杂图像生成、OCR 全量、人物身份识别。

### V6-B：Audio / Music Understanding Boundary

目标：

```text
为 music 输入定义真实内容解析的最小路径；在没有音频可解析时保持 metadata-only 诚实边界。
```

必做：

- 决定 V6 是否做 ASR、歌词/描述解析、还是仅增强 metadata schema。
- 不把曲风/情绪猜测写成无证据偏好。
- Debug 标记 music content parsed / metadata-only。

不做：

- 音乐版权内容下载、流媒体抓取、完整音频推荐系统。

### V6-C：Video Understanding Boundary

目标：

```text
为 video 输入定义关键帧 / 字幕 / metadata 的最小解析路径，避免昂贵且不可控的完整视频理解。
```

必做：

- 决定 keyframe caption、字幕文本、metadata 三者优先级。
- 记录解析来源和 evidence trace。
- 明确大文件、超时、失败降级规则。

不做：

- 长视频全量多帧理解、视频生成、实时视频分析。

### V6-D：Production Hardening & Runtime CI

目标：

```text
把 V5 留下的生产集成债务收束到测试、配置、warning 和 observability 边界。
```

必做候选：

- Pydantic/FastAPI alias warnings 清理或升级策略。
- 干净 DB integration fixture / testcontainers 可行性结论。
- real runtime smoke 与 CI memory 路径分层。
- `.env.example` / 启动说明更新。

可选：

- OTel / LangSmith 最小 trace exporter（dev-only 或 optional）。

### V6-E：Multimodal Governance Validation & Closure Prep

目标：

```text
横切验证 image/audio/video 真实解析不破坏 evidence-first、profile governance、identity scope 与 runtime boundary。
```

必做：

- `test_v6e_governance_validation.py` 或等价横切测试。
- 人工全链路验收清单。
- V6 archive gate 准备。

不做：

- V6 archive 本身（单独 closure gate）。

## 8. 关键架构决策（待确认）

### 8.1 多模态 extractor 形态

候选：

| 方案 | 优点 | 风险 | 倾向 |
| --- | --- | --- | --- |
| A 扩展现有 feature extractor | 改动小 | 多模态逻辑混杂 | 短期可用 |
| B 按 modality 拆 extractor adapter | 边界清晰，便于 mock/real runtime | 需要新增 factory | **推荐** |
| C 直接让 report LLM 读取全部媒体上下文 | 少建层 | evidence 不稳定，难治理 | 不推荐 |

### 8.2 真实 runtime 策略

候选：

| 方案 | 优点 | 风险 | 倾向 |
| --- | --- | --- | --- |
| 本地 Ollama vision / Qwen-VL 类模型 | 本地可控 | 硬件/模型可用性不稳定 | 可选 |
| 远程 vision API | 效果稳定 | key/cost/隐私 | 作为 adapter |
| 先 caption 再结构化 feature | 易审计 | 多一步延迟 | **推荐** |

### 8.3 失败语义

原则：

```text
用户明确上传图片并要求分析图片内容时，vision extraction 失败应 fail-fast 或明确 partial_failed；
用户只提供 metadata / URL 且内容不可取时，可以 metadata-only，但必须在 debug/report 中诚实标记。
```

## 9. 版本级验收标准（候选）

V6 完成时必须满足：

- 至少 image 输入具备真实内容解析路径，生成可追溯 `InputFeature`。
- music/video 的真实解析边界明确：已实现的路径可验证，未实现的路径不伪装。
- 多模态解析输出含 `promptVersion`、`modelName`、evidence，不绕过 schema validator。
- report insights 的 evidenceRefs 仍只指向当前 report inputs。
- 真实多模态 runtime / mock / metadata-only 边界在 Debug 中可见。
- profile positive evidence 不直接来自未确认或不确定的多模态解释。
- 后端全量 pytest 通过；新增 V6 governance tests 通过。
- V6 结束前有 archive gate 和 legacy issue audit。

## 10. 权威设计文档更新判断

V6-0 确认后、V6-A 实现前建议：

- `docs/20-多模态偏好建模设计文档.md`：必须扩展 image/audio/video 真实解析语义和治理不变量。
- `docs/07`：如新增媒体解析结果持久字段或表，需同步。
- `docs/09`：如 workflow 增加 modality-specific extraction step，需同步。
- `docs/10`：如新增 vision/audio prompt contract，需同步。
- `docs/11`：如新增 extractor adapter / service contract，需同步。
- `docs/13`：新增 V6 multimodal governance checks。

本轮 V6-0 暂不直接修改权威正文，仅记录判断；若用户确认 V6-0，再先扩展 `docs/20`，再进入 V6-A。

## 11. V6-0 输出物

- [x] V6 主题候选。
- [x] V5 carry_over 重分类。
- [x] V6 子阶段候选拆分。
- [x] 权威设计文档更新判断。
- [x] 用户确认 §12。

## 12. 用户确认（已接受，2026-06-23）

- [x] 接受 V6 major 主题为 **Multimodal Runtime & Production Hardening**。
- [x] 接受 V6 主线优先级：**Image → Audio/Music → Video → Hardening → Governance**。
- [x] 接受 V6-A 前必须先扩展 `docs/20-多模态偏好建模设计文档.md`。
- [x] 接受 V6 不做企业级多模态平台、复杂 LLM-as-judge dashboard、自动下载流媒体内容。
- [x] 接受真实多模态 runtime 失败不 silent fallback mock；metadata-only 必须明确标记。
- [x] 接受 V6 完成后再进入 V6 final closure / archive gate。

## 13. 当前结论

```text
V6-0 版本级调研与用户确认已完成，状态 user_confirmed / gate_passed。
下一步：先扩展 docs/20，再进入 V6-A Image Understanding Runtime。
```
