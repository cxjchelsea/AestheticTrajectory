# V7-D：Product Demo Acceptance Planning

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-24
```

## 1. 本轮定位

V7-D 是 V7 的第四个子阶段，目标是定义作品级 demo 的验收路径和展示材料清单。

本轮目标：

```text
把系统从“工程能力已存在”推进到“可以被顺畅演示、解释和验收”的产品 demo 状态。
```

V7-D 不直接做大规模前端体验改造；它先定义 demo acceptance bar，为 V8 Product Experience & Portfolio Demo 提供明确入口。

## 2. 上游依据

必须引用：

1. `docs/iterations/v7-0-production-validation-graduation-roadmap-research.md`
2. `docs/iterations/v7-a-graduation-roadmap-acceptance-bar.md`
3. `docs/iterations/v7-b-real-runtime-smoke-pack.md`
4. `docs/iterations/v7-c-golden-dataset-evaluation-pack.md`
5. `docs/evaluation/v7-c-golden-dataset-and-rubric.md`
6. `docs/14-项目展示与简历包装文档.md`
7. `docs/README.md`

## 3. 问题定义

V7-B/V7-C 已分别提供：

```text
真实 runtime smoke pack
代表样本与人工评估 rubric
```

但作品级展示还需要回答：

```text
用户从哪里开始？
演示哪条路径？
哪些页面必须稳定？
如何说明系统不是心理测试、不是推荐系统、不是无证据模型输出？
```

## 4. 系统边界

本阶段做：

- 定义 demo script。
- 定义 demo acceptance checklist。
- 定义截图/录屏/展示材料清单。
- 明确哪些前端体验问题进入 V8。
- 同步项目展示文档或 README 入口。

本阶段不做：

- 不直接重构前端页面。
- 不新增 API。
- 不改 report runtime。
- 不把 demo 文案包装成已实现 SaaS 能力。

## 5. Demo 路径候选

建议作品级 demo 路径：

```text
1. 打开首页 / 上传入口
2. 输入 3-5 条 text 或混合样本
3. 创建 analysis job
4. 查看 report
5. 查看 evidenceRefs / lowLevelFeatures
6. 提交 insight feedback
7. 查看 profile / history / timeline
8. 打开 debug，展示 runtime boundary / mock usage / evidence trace
9. 对照 V7-C rubric 说明质量复核方式
```

## 6. Demo Acceptance Checklist 候选

- [x] 用户路径能在 5-8 分钟内演示完成。
- [x] 报告页能清楚展示 summary、insights、evidenceRefs。
- [x] 反馈能保存，并能影响 profile evidence。
- [x] history / profile / timeline 至少有一个长期观察入口可展示。
- [x] debug 能展示 runtime boundary 和 mock/metadata-only 状态。
- [x] 演示说明能讲清楚项目不是心理测试。
- [x] 演示说明能讲清楚哪些是真实 runtime，哪些是 mock/metadata-only/pending。
- [x] 演示材料不声称未实现能力。

## 7. 用户确认（已接受，2026-06-24）

- [x] 接受 V7-D 先做 demo acceptance planning，不直接大规模改前端。
- [x] 接受 V8 再进入 Product Experience & Portfolio Demo 实现。
- [x] 接受 demo 必须展示证据链、反馈、profile 或 timeline，而不只是报告页。
- [x] 接受 debug/runtime boundary 作为作品级可信度展示的一部分。

## 8. AI 生成顺序

确认后建议按以下顺序执行：

1. 读取当前前端页面和展示文档。
2. 定义 demo script。
3. 定义 demo acceptance checklist。
4. 定义 V8 前端体验 backlog。
5. 更新 `docs/14`、`docs/README.md`、`docs/12`、`docs/15`。

## 9. 当前结论

```text
V7-D 已完成 Product Demo Acceptance Planning，状态 ready_for_validation / accepted_auto。
本轮结果：
- 新增 `docs/demo/v7-d-product-demo-acceptance.md`。
- 定义 5-8 分钟 demo script。
- 定义 demo acceptance checklist。
- 定义截图/录屏/展示文案清单。
- 定义 V8 Product Experience backlog。
- `docs/14` 已同步作品级 demo 验收入口。
- 未改前端 runtime 代码。
```

## 10. 本轮实现记录（2026-06-24）

- V7-D demo acceptance 文档已落地。
- Demo 路径覆盖 Home、Upload、Analysis、Report、Feedback、Profile/History/Timeline、Debug、V7-C rubric。
- V8 backlog 已记录：
  - Demo mode seed samples。
  - Evidence display polish。
  - Runtime boundary badge。
  - Feedback state clarity。
  - Profile empty state。
  - Timeline demo path。
  - Screenshot-friendly layout。
  - Evaluation summary panel。
- 本阶段不涉及自动化测试运行。
