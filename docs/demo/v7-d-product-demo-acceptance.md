# V7-D Product Demo Acceptance

## 1. 文档状态

```text
状态：ready_for_validation / accepted_auto
创建日期：2026-06-24
适用版本：V7-D
```

## 2. 文档职责

本文件定义作品级 demo 的演示脚本、验收清单、展示素材清单和 V8 产品体验 backlog。

它用于：

- 让项目可以被稳定演示。
- 让观看者理解系统不是心理测试、不是推荐系统、不是无证据模型输出。
- 为 V8 Product Experience & Portfolio Demo 明确实现入口。

它不用于：

- 声称当前已具备 SaaS 级生产运营能力。
- 替代真实 runtime smoke。
- 替代 V7-C evaluation rubric。
- 指示前端现在必须大规模重构。

## 3. 5-8 分钟 Demo Script

### 3.1 开场：项目定位（30 秒）

讲述：

```text
这是 Aesthetic Trajectory，一个面向长期个性化 AI 的多模态审美偏好建模系统。
它不是给用户做心理测试，也不是推荐系统，而是观察用户输入中的审美结构，并用证据支持解释。
```

展示：

- `HomePage`
- 项目一句话定义
- “开始上传 / 查看历史 / 轻量画像 / 审美时间轴”入口

验收点：

- 观看者能理解项目不是人格诊断。
- 观看者能理解核心是“长期审美形成”，不是一次性标签。

### 3.2 输入：创建一组样本（60-90 秒）

路径：

```text
Home -> Upload
```

建议使用 V7-C `text-basic-001` 或 `mixed-multimodal-001` 的简化版本：

```text
灰蓝色房间 / 空走廊 / 克制服装
```

讲述：

```text
这里输入的是用户近期被吸引的审美样本。系统要求多个样本，是为了观察跨输入结构，而不是从单个样本给用户贴标签。
```

验收点：

- 能创建 3 条以上输入。
- 输入类型和内容在 UI 中可理解。
- 如果使用 image/music/video metadata，必须说明当前是否为 mock / metadata-only / user notes。

### 3.3 分析：运行 workflow（45-60 秒）

路径：

```text
Upload -> AnalysisJobPage
```

讲述：

```text
系统会保存输入、创建分析任务、提取底层特征、生成 embedding / 分组 / 报告。默认演示环境可以不依赖外部模型，真实 runtime smoke 在 V7-B 中单独记录。
```

验收点：

- 分析状态有可理解的进度反馈。
- 后端不可用时 fallback 只作为 dev/demo 行为说明，不应包装为生产能力。

### 3.4 报告：解释、证据与不确定性（2 分钟）

路径：

```text
Analysis -> ReportDetailPage
```

重点展示：

- summary
- lowLevelFeatures
- similarityGroups
- possibleInterpretations
- insights
- evidenceRefs / evidence inputs
- disclaimer / uncertainty

讲述：

```text
报告先展示系统观察到的底层特征，再给出可能解释。每条洞察都需要 evidenceRefs，解释必须使用“可能、倾向、在这组输入中”这类不绝对化语言。
```

验收点：

- 报告能清楚展示输入证据。
- 洞察不包含人格、心理、能力、命运式判断。
- 如果是 metadata-only 或 placeholder，报告不得伪装成真实媒体内容解析。

### 3.5 反馈：用户修正系统解释（45-60 秒）

路径：

```text
ReportDetailPage -> FeedbackPanel
```

讲述：

```text
用户反馈是长期画像的关键治理机制。系统不能未经用户确认就把模型解释写成稳定偏好。
```

验收点：

- 可以对 insight 提交反馈。
- feedback 会成为 profile evidence。
- 被否定的解释不进入正向稳定偏好。

### 3.6 长期观察：Profile / History / Timeline（90 秒）

路径：

```text
Report -> History / Profile / Timeline
```

讲述：

```text
系统不是只做一次报告，而是把历史报告、反馈和时间线组织成长期观察。它描述“系统观察到的倾向”，而不是定义用户本质。
```

验收点：

- History 能展示历史报告入口。
- Profile 能展示 evidence-backed profile 或空状态。
- Timeline 能展示审美轨迹事件或说明当前数据不足。

### 3.7 Debug / Trust Boundary（60 秒）

路径：

```text
ReportDetailPage -> Developer Debug 区域（开发环境）
```

重点展示：

- mockUsage
- boundaryWarnings
- workflowTrace
- fallbackEvents
- schemaValidation
- retrievalTrace

讲述：

```text
Debug 面板用于证明系统没有把 mock、metadata-only 或 fallback 伪装成真实能力。真实 runtime smoke 在 V7-B 中单独作为 optional local gate。
```

验收点：

- mock / real / disabled / metadata-only boundary 可见。
- fallback 不伪造业务事实。
- evidence trace 可追踪。

### 3.8 评估：如何证明质量（30-45 秒）

展示：

```text
docs/evaluation/v7-c-golden-dataset-and-rubric.md
```

讲述：

```text
除了自动测试，V7-C 定义了代表样本和人工 rubric，用来复核 evidence grounding、interpretation usefulness、specificity、governance safety 和 modality honesty。
```

验收点：

- 观看者能理解项目质量如何被复核。
- 观看者能理解哪些能力是 pending 或 carry-over。

## 4. Demo Acceptance Checklist

### 4.1 必须通过

- [ ] Demo 可在 5-8 分钟内完成。
- [ ] 用户能完成输入 -> 分析 -> 报告路径。
- [ ] 报告至少展示 summary、lowLevelFeatures、insights、evidenceRefs。
- [ ] 至少一次 feedback 可被提交或说明当前 demo 为 mock fallback。
- [ ] 至少一个长期观察入口可展示：History / Profile / Timeline。
- [ ] Debug 可展示 runtime boundary、mock usage 或 boundary warnings。
- [ ] 演示中明确说明 mock / metadata-only / pending_validation。
- [ ] 演示中不声称系统做人格诊断、心理评估或推荐消费。

### 4.2 建议通过

- [ ] 使用 V7-C 的一个 representative sample。
- [ ] 截图覆盖 Home、Upload、Report、Profile/Timeline、Debug。
- [ ] 演示后能指向 V7-B smoke pack 和 V7-C rubric。
- [ ] 演示中能说明 V8 将打磨的前端体验问题。

### 4.3 不阻塞 V7-D

- [ ] 真实 vision 模型未部署。
- [ ] 真实 audio/video parser 未实现。
- [ ] LangSmith / OTel / Sentry 未接入。
- [ ] 前端 UI 仍需要 V8 打磨。

## 5. 展示素材清单

### 5.1 截图

- Home：项目定位与入口。
- Upload：样本输入。
- Analysis：分析状态。
- Report：summary / insights / evidence。
- Feedback：用户反馈。
- Profile 或 Timeline：长期观察入口。
- Debug：runtime boundary / mock usage。
- Evaluation 文档：V7-C rubric。

### 5.2 录屏

建议录制 1 条 5-8 分钟 demo：

```text
home -> upload -> analysis -> report -> feedback -> profile/timeline -> debug -> evaluation rubric
```

### 5.3 展示文案

推荐标题：

```text
Aesthetic Trajectory：长期个性化 AI 的多模态审美偏好建模系统
```

推荐副标题：

```text
从多模态输入中提取审美结构，用证据支持解释，并通过反馈形成长期审美轨迹。
```

禁止文案：

- AI 看透你的审美人格。
- 上传图片测出你的灵魂。
- 自动判断你是什么类型的人。
- AI 告诉你真正喜欢什么。

## 6. V8 Product Experience Backlog

V7-D 不直接改前端，但为 V8 记录 backlog：

| Backlog | 目标 | 优先级 |
| --- | --- | --- |
| Demo mode seed samples | 一键加载 V7-C representative sample | 高 |
| Evidence display polish | 让 evidenceRefs 与输入证据更直观 | 高 |
| Runtime boundary badge | 在报告/debug 中更清楚展示 mock / metadata-only / real | 高 |
| Feedback state clarity | 反馈后清楚显示 profile evidence 影响 | 中 |
| Profile empty state | 数据不足时解释为什么还没有稳定画像 | 中 |
| Timeline demo path | 让时间线在少量样本下也可解释 | 中 |
| Screenshot-friendly layout | 作品集截图更稳定 | 中 |
| Evaluation summary panel | 把 V7-C rubric 结果用轻量卡片展示 | 低 / V9 |

## 7. V7-D 结论

```text
V7-D Product Demo Acceptance 已定义。
当前项目具备作品级 demo 验收脚本。
V8 应进入 Product Experience & Portfolio Demo 实现。
```
