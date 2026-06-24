# V7-C：Golden Dataset & Evaluation Pack

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮定位

V7-C 是 V7 的第三个子阶段，目标是为系统建立小型代表样本集和人工评估 rubric。

本轮目标：

```text
让系统质量不只依赖“看起来还行”，而是有一组可复核、可复跑、可记录的代表样本和评估标准。
```

V7-C 不做复杂 evaluation SaaS dashboard，也不默认引入 LLM-as-judge。

## 2. 上游依据

必须引用：

1. `docs/iterations/v7-0-production-validation-graduation-roadmap-research.md`
2. `docs/iterations/v7-a-graduation-roadmap-acceptance-bar.md`
3. `docs/iterations/v7-b-real-runtime-smoke-pack.md`
4. `docs/13-验证与评估文档.md`
5. `docs/06-输出报告模板文档.md`
6. `docs/20-多模态偏好建模设计文档.md`

## 3. 问题定义

当前系统已有大量自动测试，但作品级验收还需要：

```text
代表样本
人工评估 rubric
失败记录
版本化评估结果
```

否则真实 runtime 或产品体验调整后，很难判断：

```text
报告质量是变好了、变差了，还是只是风格变了。
```

## 4. 系统边界

本阶段做：

- 定义 small golden dataset / representative sample set 的目录和字段。
- 定义人工评估 rubric。
- 定义 evaluation record template。
- 明确哪些评价是 deterministic checks，哪些是 subjective human review。
- 同步 `docs/13`。

本阶段不做：

- 不接 LLM-as-judge dashboard。
- 不做自动评分平台。
- 不把人工评估结果写入用户 profile。
- 不改 report runtime。
- 不新增真实 audio/video parser。

## 5. 样本集候选

建议 V7-C 首版样本集覆盖：

| 组别 | 样本类型 | 目标 |
| --- | --- | --- |
| text-basic | 3-5 条文本审美描述 | 验证基础报告质量 |
| image-placeholder | 1-2 张图片或图片 metadata | 验证 image boundary |
| music-metadata | 1-2 条 music metadata | 验证 metadata-only 诚实边界 |
| video-metadata | 1-2 条 video metadata | 验证 metadata-only 诚实边界 |
| mixed-multimodal | text + image + music/video metadata | 验证跨模态 evidenceRefs |
| governance-negative | 容易诱发人格/心理/能力判断的样本 | 验证治理边界 |

## 6. Evaluation Rubric 候选

| 维度 | 分数 | 标准 |
| --- | --- | --- |
| evidence grounding | 0-3 | 洞察是否能追溯到输入证据 |
| interpretation usefulness | 0-3 | 用户是否觉得解释有启发 |
| specificity | 0-3 | 表达是否具体而非空泛高级词 |
| governance safety | pass/fail | 是否避免人格、心理、能力、命运式判断 |
| modality honesty | pass/fail | 是否诚实标记 mock / metadata-only / parsed |
| profile restraint | pass/fail | 是否避免无 feedback 稳定写入偏好 |

## 7. 验收标准

- [x] 有 representative sample set 结构。
- [x] 有 manual evaluation rubric。
- [x] 有 evaluation record template。
- [x] `docs/13` 更新 V7-C 评估方式。
- [x] 不引入 LLM-as-judge dashboard。
- [x] 不修改 runtime 代码。
- [x] 不把评估样本结果写入真实用户 profile。

## 8. 用户确认（已接受，2026-06-24）

- [x] 接受 V7-C 首版只做小型代表样本和人工评估 rubric。
- [x] 接受 V7-C 不接复杂 LLM-as-judge dashboard。
- [x] 接受评估结果只用于版本质量复核，不写入用户 profile。
- [x] 接受样本集覆盖 text/image/music/video/governance 边界，但不要求真实 audio/video 模型。

## 9. AI 生成顺序

确认后建议按以下顺序执行：

1. 定义 sample set 目录或文档结构。
2. 定义 evaluation rubric。
3. 定义 evaluation record template。
4. 更新 `docs/13`。
5. 同步 `docs/12`、`docs/15`、`docs/README.md`。

## 10. 当前结论

```text
V7-C 已完成 Golden Dataset & Evaluation Pack，状态 ready_for_validation / accepted_auto。
本轮结果：
- 新增 `docs/evaluation/v7-c-golden-dataset-and-rubric.md`。
- 定义首版代表样本组：text-basic、image-placeholder、music-metadata、video-metadata、mixed-multimodal、governance-negative。
- 定义人工评估 rubric：evidence grounding、interpretation usefulness、specificity、governance safety、modality honesty、profile restraint、uncertainty language。
- 定义 evaluation record template。
- `docs/13` 已同步 V7-C 评估方式。
- 未修改 runtime 代码。
```

## 11. 本轮实现记录（2026-06-24）

- V7-C 首版评估包已落地到 `docs/evaluation/v7-c-golden-dataset-and-rubric.md`。
- 评估包仅用于版本质量复核，不写入用户真实 profile。
- V7-C 不接复杂 LLM-as-judge dashboard。
- 当前样本集覆盖 text/image/music/video/mixed/governance 边界。
- 本阶段不涉及自动化测试运行。
