# V6-E：Multimodal Governance Validation & Closure Prep

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V6-E 目标：

```text
横切验证 image/music/video runtime 不破坏 evidence-first、profile governance、identity scope、runtime boundary 和 debug 可见性，并为 V6 final closure / archive gate 做准备。
```

V6-E 是治理验证和收口准备阶段，不是最终归档阶段。

## 2. 上游依据

必须引用：

1. `docs/iterations/v6-0-multimodal-runtime-production-hardening-research.md`
2. `docs/iterations/v6-a-image-understanding-runtime.md`
3. `docs/iterations/v6-b-audio-music-understanding-boundary.md`
4. `docs/iterations/v6-c-video-understanding-boundary.md`
5. `docs/iterations/v6-d-production-hardening-runtime-ci.md`
6. `docs/20-多模态偏好建模设计文档.md` §3.5 / §7
7. `docs/13-验证与评估文档.md` §15.3 / §15.4
8. V5-E governance validation 测试模式

## 3. 问题定义

当前状态：

- V6-A/B/C 已建立 image/music/video modality runtime baseline。
- V6-D 已让默认 pytest baseline 干净：`146 passed`。
- 多模态 feature extractor 有各自单元测试，但还缺一次 V6 级横切治理验证。
- V6-A 真实 vision 模型人工验收仍为 `real_model_pending`。
- V6 final closure / archive gate 需要提前准备 legacy issue audit，但本轮不直接归档。

V6-E 解决：

```text
用横切测试确认多模态 runtime 不会绕过 evidenceRefs、profile builder、用户 scope、debug boundary 和 mock/metadata-only 诚实性；
整理 V6 final closure 前必须处理或分类的 legacy issues。
```

## 4. 治理验证范围

### 4.1 Evidence Traceability

必须验证：

- report `evidenceRefs` 只引用当前 report inputs。
- image/music/video feature 的 `sampleEvidence` 来自当前 input metadata、用户文本或明确 runtime 输出。
- external source、profile item、knowledge context 不得直接伪装成 input evidence。

### 4.2 Profile Governance

必须验证：

- 多模态 input 不直接写入 stable profile positive evidence。
- profile positive evidence 仍必须经过 report / feedback / profile builder 链路。
- metadata-only / placeholder / low confidence feature 不得形成 stable profile item。

### 4.3 Identity Scope

必须验证：

- 不同匿名 session / user 之间不能访问对方 report、debug、profile、input 相关资源。
- 多模态 upload file / fileUrl 不绕过 user scope。

### 4.4 Runtime Boundary

必须验证：

- image/music/video runtime 的 mock / metadata-only / disabled / real-placeholder 状态在 Debug 中可见。
- disabled runtime fail-fast，不 silent fallback mock。
- metadata-only runtime 不声称真实内容解析。
- mock runtime 必须标记 dev-only。

### 4.5 Diagnostic / Sensitive Claim Boundary

必须验证：

- 不输出人格诊断、心理疾病、能力判断、命运式判断。
- image/video 不做人脸身份识别、年龄/性别/身份推断。
- music/video 不从 title / URL 推测真实音频/画面内容。

## 5. 系统边界

### 5.1 本轮包含

- 新增 `test_v6e_governance_validation.py` 或等价横切测试。
- 覆盖 image/music/video 默认 runtime 的 evidence / debug / boundary。
- 覆盖 disabled fail-fast 的治理路径。
- 覆盖 metadata-only 不伪装真实解析。
- 更新 V6 legacy issue 初稿。
- 更新 V6 closure prep 入口文档。

### 5.2 本轮不做

- 不做 V6 final archive。
- 不要求真实 vision/audio/video 模型部署。
- 不接入 production observability 平台。
- 不新增新 modality runtime。
- 不重构 report/profile 核心链路，除非横切测试暴露真实缺陷。

## 6. 候选实现项

优先级建议：

1. 新增 V6-E 横切 integration tests：
   - 默认 runtime workflow；
   - debug mockUsage / boundaryWarnings；
   - evidenceRefs 范围；
   - diagnostic phrase guard。
2. 新增 disabled runtime fail-fast tests：
   - `IMAGE_FEATURE_RUNTIME=disabled`
   - `MUSIC_FEATURE_RUNTIME=disabled`
   - `VIDEO_FEATURE_RUNTIME=disabled`
3. 新增 metadata-only honesty tests：
   - music/video metadata-only 不包含 audio/video claim。
4. 整理 V6 legacy issue 初稿：
   - V6-A real vision validation pending；
   -真实 audio/video runtime 后续；
   - optional Postgres/Chroma/Ollama smoke；
   - production observability optional。
5. 更新 docs/13 / docs/15 / docs/12。

## 7. 验收标准

### 7.1 自动验证

- [x] V6-E 横切 governance tests 通过。
- [x] 后端全量 pytest 通过。
- [x] evidenceRefs 只引用当前 report inputs。
- [x] metadata-only / mock / disabled runtime boundary 在 debug 中可见。
- [x] disabled runtime fail-fast，不 silent fallback mock。
- [x] 多模态输入不直接写入 stable profile positive evidence。
- [x] 不输出人格、心理、能力、命运、身份推断类表达。

### 7.2 人工验证

- [ ] 默认 memory/mock/metadata-only runtime 可跑通。
- [ ] Debug 中可看到 image/music/video runtime 状态。
- [ ] V6 legacy issue list 初稿可用于 final closure。

## 8. AI 生成顺序

1. 读取 V5-E governance validation 测试模式。
2. 读取 V6-A/B/C/D runtime 与测试。
3. 新增 V6-E 横切测试。
4. 如测试暴露缺陷，做最小修复。
5. 运行 V6-E 定向测试与后端全量 pytest。
6. 更新 `docs/13`、`docs/15`、`docs/12`、`README`。
7. 准备 V6 final closure / archive gate 的下一步建议。

## 9. 用户确认（已接受，2026-06-23）

- [x] 接受 V6-E 只做横切治理验证和 closure prep，不做 V6 final archive。
- [x] 接受 V6-A real vision 仍可作为 `pending_validation`，不阻塞默认 pytest。
- [x] 接受真实 audio/video runtime 继续作为后续 extension，不在 V6-E 强制实现。
- [x] 接受 V6-E 完成后进入 V6 final closure / archive gate。
- [x] 接受如横切测试暴露治理缺陷，优先做最小修复而不是扩大 scope。

## 10. 当前结论

```text
V6-E 已完成横切 governance validation 与 closure prep，状态 ready_for_validation / accepted_auto。
本轮结果：
- 新增 V6-E 横切 integration tests，覆盖 evidenceRefs、profile governance、identity scope、runtime boundary、disabled fail-fast。
- 修复 profile governance：feature-only profile item 不能在没有 feedback 的情况下变成 stable。
- 整理 V6 final closure prep legacy issue 初稿。

自动验证：
- python -m pytest backend/app/tests/unit/test_profile_builder.py backend/app/tests/integration/test_v6e_multimodal_governance_validation.py -q
  11 passed
- python -m pytest backend/app/tests/unit/test_profile_builder.py backend/app/tests/integration/test_v6e_multimodal_governance_validation.py backend/app/tests/unit/test_v6a_image_feature_runtime.py backend/app/tests/unit/test_v6b_audio_music_feature_runtime.py backend/app/tests/unit/test_v6c_video_feature_runtime.py backend/app/tests/unit/test_v6d_runtime_hardening.py backend/app/tests/integration/test_v6d_upload_isolation.py backend/app/tests/integration/test_v5e_governance_validation.py -q
  40 passed
- python -m pytest backend/app/tests -q
  151 passed
```

## 11. 本轮实现记录（2026-06-23）

- 新增 `backend/app/tests/integration/test_v6e_multimodal_governance_validation.py`。
- 横切验证默认多模态 workflow：
  - image mock / music metadata-only / video metadata-only runtime boundary 在 debug 中可见；
  - report `evidenceRefs` 只引用当前 input ids；
  - report insight 不包含人格、心理、能力、命运式表达；
  - low-level features 明确标记 image placeholder、music/video metadata-only。
- 横切验证 profile governance：
  - feature-only profile item 不能在无 feedback 时成为 stable；
  - feedback 后 profile evidence 必须包含 feedback evidence，且不把 input id 直接当 profile evidence。
- 横切验证 identity scope：
  - report、job、debug、profile 跨用户不可访问；
  - upload file 跨用户不可读取。
- 横切验证 disabled runtime：
  - `MUSIC_FEATURE_RUNTIME=disabled` 下 analysis job fail-fast；
  - 不生成 report，不 silent fallback mock。
- 最小修复 `profile_builder`：feature-only item 即使正向证据重复，也最高保持 `recent`，不能直接成为 `stable`。

## 12. V6 final closure prep：legacy issue 初稿

| 项目 | 状态 | 建议归类 | 目标 |
| --- | --- | --- | --- |
| V6-A 真实 vision 模型人工验收 | pending_validation | closure gate 判断是否继续 pending 或转 carry_over | V6 final closure |
| 真实 audio/music runtime（ASR / audio feature） | carry_over | 后续扩展，不阻塞 V6 默认 baseline | V7+ / optional runtime |
| 真实 video runtime（keyframe / remote video） | carry_over | 后续扩展，不阻塞 V6 默认 baseline | V7+ / optional runtime |
| Postgres / Chroma / Ollama smoke 自动化 | carry_over | 当前为 optional local path | V7 hardening |
| LangSmith / OTel / Sentry production observability | carry_over / optional | 当前未接入生产观测平台 | V7+ |
| V6 final archive docs | pending | V6-E 后进入 closure gate | V6 final closure |
