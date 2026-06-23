# V6-C：Video Understanding Boundary

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V6-C 目标：

```text
为 video 输入定义关键帧 / 字幕 / metadata 的最小可信解析路径，并避免把昂贵且不可控的完整视频理解伪装成已完成能力。
```

V6-C 不追求完整视频理解平台，而是先把 video 输入从“标题/链接占位”升级为可区分的：

```text
metadata_only
subtitle_or_description_parsed
keyframe_placeholder
video_failed
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v6-0-multimodal-runtime-production-hardening-research.md`
2. `docs/20-多模态偏好建模设计文档.md` §3.1-§3.5 / §7
3. `docs/10-Prompt Contract 与结构化输出规范.md`
4. `docs/13-验证与评估文档.md` §15.3 / §15.4
5. V6-A image runtime adapter / validator / debug boundary
6. V6-B music runtime metadata-only / text-notes / disabled 模式

## 3. 问题定义

当前状态：

- `video` input 已存在，但只要求 `title` 或 `fileUrl`。
- workflow 中 video feature 仍由 fallback mock feature extractor 生成泛化占位。
- 系统不能诚实声称“看过视频画面”或“理解了剪辑/运动/镜头”。

V6-C 解决：

```text
当用户登记 video 输入时，系统能明确区分：
1. 只使用 title / description / URL metadata；
2. 使用用户提供字幕、简介、分镜说明或观看笔记；
3. keyframe / video parser 尚未启用或失败；
并把这个边界进入 InputFeature、debug 和治理测试。
```

## 4. 方案选择

### 4.1 推荐路径

首版推荐：

```text
VideoFeatureExtractor adapter
→ 若 contentText / description 中包含用户提供字幕、简介、分镜说明或观看笔记，则走 text-derived video feature
→ 若只有 title / fileUrl，则 metadata_only
→ 保留 disabled / mock boundary
→ 输出 InputFeature
→ validator 检查 evidence 与治理边界
```

理由：

- 当前没有稳定视频模型，也没有 keyframe extraction pipeline。
- 长视频解析成本高、超时和失败面大。
- 不应自动下载流媒体或版权视频。
- 用户主动提供的字幕、简介、分镜说明、观看笔记是可追溯证据。
- metadata-only 是 video 输入的合法路径，但必须显性标记。

### 4.2 Runtime 候选

| Runtime | 用途 | V6-C 判断 |
| --- | --- | --- |
| `mock` | CI / dev baseline | 保留，必须 dev-only 标记 |
| `metadata_only` | 只使用 title / description / URL | 首版推荐默认真实边界 |
| `text_notes` | 用户提供 subtitle / description / shot notes | 首版可实现 |
| `disabled` | 禁止 video 内容解析 | 用于 fail-fast / boundary 测试 |
| `keyframe_local` | 本地抽帧 + image runtime | 后置 spike，不作为首版硬依赖 |
| `remote_video` | 远程视频理解 API | 后置，不作为首版硬依赖 |

V6-C 默认建议：

```text
VIDEO_FEATURE_RUNTIME=metadata_only|text_notes|mock|disabled
```

不建议首版默认启用：

```text
VIDEO_FEATURE_RUNTIME=keyframe_local
```

除非用户已经接受本地视频读取、抽帧、文件大小限制、超时、模型成本与输出治理。

## 5. 系统边界

### 5.1 本轮包含

- 新增 video feature runtime 配置。
- 新增 `VideoFeatureExtractor` 或等价 adapter。
- 让 video 输入能输出明确解析状态：
  - `metadata_only`
  - `subtitle_or_description_parsed`
  - `placeholder`
  - `failed`
- 用户提供 subtitle / description / shot notes 时，可以作为 text-derived video evidence。
- 只有 title / fileUrl 时，不声称解析过画面、镜头或运动。
- Debug 中可见 mock / metadata_only / text_notes / disabled 边界。
- schema / governance validator 阻止无证据视觉、剪辑、镜头、人物状态、人格或心理判断。

### 5.2 本轮不做

- 不下载 YouTube / B站 / 小红书 / TikTok / Vimeo 等流媒体视频。
- 不绕过版权或登录授权抓取视频。
- 不做长视频全量多帧理解。
- 不做视频生成、实时视频分析、目标跟踪。
- 不做人脸身份识别、年龄/性别/身份推断。
- 不从标题猜测镜头、剪辑、色彩、运动或情绪事实。

## 6. 契约设计

V6-C 输出仍复用 `InputFeature`：

```text
InputFeature
├── inputId
├── featureType = video
├── lowLevelFeatures
│   ├── videoParsingStatus
│   ├── sourceTextType
│   ├── visualNarrative / sceneImagery
│   └── pacingImpression / motionImpression（仅在有文本证据时）
├── sampleEvidence
├── promptVersion
└── modelName
```

建议 feature key：

| key | 说明 | evidence 要求 |
| --- | --- | --- |
| `videoParsingStatus` | `metadata_only` / `subtitle_or_description_parsed` / `placeholder` / `failed` | 必须说明来源 |
| `sourceTextType` | `title` / `description` / `subtitle` / `shot_notes` / `notes` | 必须引用用户提供文本 |
| `sceneImagery` | 字幕/简介/分镜中的场景意象 | 仅 text_notes 可用 |
| `pacingImpression` | 用户文本明确提到快慢/节奏时可用 | 不从标题猜测 |
| `visualNarrative` | 文本证据支持的叙事结构 | 不声称模型看过画面 |

## 7. API / 数据影响

首版建议不改数据库：

```text
video input 的 contentText / description 可承载用户主动提供的 subtitle / description / shot notes。
```

如果后续需要明确字段，可在 V6-C 后半段或 V6-D hardening 中评估：

```text
videoContentKind = title_only | description | subtitle | shot_notes | transcript
```

首版不建议现在改 API，因为现有 `CreateInputRequest` 已支持：

- `type=video`
- `contentText`
- `title`
- `description`
- `fileUrl`

## 8. 失败语义

| 场景 | 处理 |
| --- | --- |
| `VIDEO_FEATURE_RUNTIME=metadata_only` 且只有 title/fileUrl | 成功，但 feature 标记 `metadata_only` |
| 用户提供 subtitle/description/shot notes | 成功，feature 标记 `subtitle_or_description_parsed` |
| `VIDEO_FEATURE_RUNTIME=disabled` 遇到 video input | fail-fast |
| `VIDEO_FEATURE_RUNTIME=keyframe_local` 后续启用但抽帧或模型失败 | fail-fast 或 explicit `failed`，不得 silent fallback mock |
| metadata-only 输出试图生成“看见镜头/剪辑/画面/运动” | validator 拦截 |
| 输出人脸身份、年龄/性别推断、人格/心理/能力/命运判断 | validator 拦截 |

## 9. 验收标准

### 9.1 自动验证

- [x] video metadata-only path 测试通过。
- [x] video text-notes / subtitle path 测试通过。
- [x] disabled path fail-fast 测试通过。
- [x] validator 拦截无证据 visual / motion / editing claim。
- [x] governance 测试确认不输出身份、人格、心理、能力、命运式判断。
- [x] Debug `mockUsage` / boundary warning 标记 video runtime。
- [x] 后端全量 pytest 通过。

### 9.2 人工验证

- [ ] 创建只有 title 的 video input，报告/debug 不声称已看视频画面。
- [ ] 创建含字幕/简介/分镜说明的 video input，报告可引用用户提供文本证据。
- [ ] 配置 disabled runtime，video 输入应失败而不是 silent fallback mock。
- [ ] 若未来部署 keyframe/video runtime，再补真实视频解析人工验收。

## 10. AI 生成顺序

1. 读取 V6-A / V6-B factory、extractor、validator 流程。
2. 新增 video runtime 配置。
3. 新增 `VideoFeatureExtractor` mock / metadata_only / text_notes / disabled。
4. 将 factory 扩展为 image + music + video modality routing。
5. 增加 video feature validator。
6. 更新 Debug mockUsage / boundary warning。
7. 补充 unit / integration governance 测试。
8. 更新 `.env.example`、`启动说明.md`、`docs/13`、`docs/15`。

## 11. 用户确认（已接受，2026-06-23）

- [x] 接受 V6-C 首版不做长视频全量理解、抽帧 pipeline 或实时视频分析。
- [x] 接受 `metadata_only` 是 video 的合法默认路径，但必须显性标记。
- [x] 接受用户提供 subtitle / description / shot notes 可以作为 text-derived video evidence。
- [x] 接受不抓取流媒体或版权视频内容。
- [x] 接受后续如接入真实 keyframe/video runtime，失败不得 silent fallback mock。
- [x] 接受 V6-C 完成后进入 V6-D Production Hardening & Runtime CI。

## 12. 当前结论

```text
V6-C 已完成 metadata_only + text_notes + disabled + mock 边界实现，状态 ready_for_validation / accepted_auto。
自动验证：
- python -m pytest backend/app/tests/unit/test_v6c_video_feature_runtime.py -q
  8 passed
- python -m pytest backend/app/tests/unit/test_feature_schema.py backend/app/tests/unit/test_v6a_image_feature_runtime.py backend/app/tests/unit/test_v6b_audio_music_feature_runtime.py backend/app/tests/unit/test_v6c_video_feature_runtime.py backend/app/tests/integration/test_api_flow.py backend/app/tests/integration/test_v5e_governance_validation.py -q
  29 passed, 3 warnings
- python -m pytest backend/app/tests -q
  142 passed, 5 warnings

V6-C 首版不依赖真实 keyframe/video 模型；未来如部署真实 video runtime，另行进入后续子阶段或 hardening 验收。
```

## 13. 本轮实现记录（2026-06-23）

- 新增 `VIDEO_FEATURE_RUNTIME=metadata_only|text_notes|mock|disabled`。
- 新增 `VideoFeatureExtractor` 等价实现：metadata-only、text-notes、mock placeholder、disabled fail-fast。
- 扩展 default modality factory：image 走 V6-A runtime，music 走 V6-B runtime，video 走 V6-C runtime，text 保持既有 fallback。
- 新增 video feature governance validator：
  - metadata-only 不得声称看见镜头、画面、剪辑、运动、光线、色彩等真实视频内容；
  - 不得输出身份、年龄、性别、人格、心理、能力、命运式判断。
- Debug `mockUsage` / boundary warning 可显示 video runtime 边界。
- 更新 `backend/.env.example` 与 `backend/启动说明.md`。
