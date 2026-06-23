# V6-B：Audio / Music Understanding Boundary

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V6-B 目标：

```text
为 music 输入定义真实内容解析的最小可信路径，并在没有音频或授权内容可解析时保持 metadata-only 诚实边界。
```

V6-B 不追求完整音乐理解平台，而是先把 music 输入从“标题/链接占位”升级为可区分的：

```text
metadata_only
lyrics_or_transcript_parsed
audio_placeholder
audio_failed
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v6-0-multimodal-runtime-production-hardening-research.md`
2. `docs/20-多模态偏好建模设计文档.md` §3.1-§3.5 / §7
3. `docs/10-Prompt Contract 与结构化输出规范.md`
4. `docs/13-验证与评估文档.md` §15.3 / §15.4
5. V6-A `ImageFeatureExtractor` adapter / factory / governance validator 实现

## 3. 问题定义

当前状态：

- `music` input 已存在，但只要求 `title` 或 `fileUrl`。
- workflow 中 music feature 仍由 mock feature extractor 给出泛化占位特征。
- 系统不能诚实声称“听过歌曲”或“理解音频内容”。

V6-B 解决：

```text
当用户登记 music 输入时，系统能明确区分：
1. 只使用 title / description / URL metadata；
2. 使用用户提供的 lyrics / transcript / notes 文本；
3. 真实 audio parser 尚未启用或失败；
并把这个边界进入 InputFeature、debug 和治理测试。
```

## 4. 方案选择

### 4.1 推荐路径

首版推荐：

```text
AudioMusicFeatureExtractor adapter
→ 若 contentText / description 中包含用户提供歌词、听感笔记或文字描述，则走 text-derived music feature
→ 若只有 title / fileUrl，则 metadata_only
→ 保留 disabled / mock boundary
→ 输出 InputFeature
→ validator 检查 evidence 与治理边界
```

理由：

- 当前没有稳定 ASR / audio feature 模型。
- 不应抓取流媒体或版权内容。
- 用户主动提供的歌词、转录、笔记是可追溯证据。
- metadata-only 是 music 输入的合法路径，但必须在 debug / feature 中明示。

### 4.2 Runtime 候选

| Runtime | 用途 | V6-B 判断 |
| --- | --- | --- |
| `mock` | CI / dev baseline | 保留，必须 dev-only 标记 |
| `metadata_only` | 只使用 title / description / URL | 首版推荐默认真实边界 |
| `text_notes` | 用户提供 lyrics / transcript / notes | 首版可实现 |
| `disabled` | 禁止 music 内容解析 | 用于 fail-fast / boundary 测试 |
| `asr_local` | 本地 ASR 或音频特征模型 | 后置 spike，不作为首版硬依赖 |
| `remote_audio` | 远程音频理解 API | 后置，不作为首版硬依赖 |

V6-B 默认建议：

```text
MUSIC_FEATURE_RUNTIME=metadata_only|text_notes|mock|disabled
```

不建议首版默认启用：

```text
MUSIC_FEATURE_RUNTIME=asr_local
```

除非用户已经部署可用 ASR / audio feature 模型，并接受本地音频文件读取、超时、文件大小与模型输出治理。

## 5. 系统边界

### 5.1 本轮包含

- 新增 music feature runtime 配置。
- 新增 `AudioMusicFeatureExtractor` 或等价 adapter。
- 让 music 输入能输出明确解析状态：
  - `metadata_only`
  - `lyrics_or_transcript_parsed`
  - `placeholder`
  - `failed`
- 用户提供 lyrics / transcript / notes 时，可以作为 text-derived music evidence。
- 只有 title / fileUrl 时，不声称解析过音频。
- Debug 中可见 mock / metadata_only / text_notes / disabled 边界。
- schema / governance validator 阻止无证据曲风、人格、心理、能力或命运判断。

### 5.2 本轮不做

- 不下载 Spotify / 网易云 / B站 / YouTube 等流媒体内容。
- 不绕过版权或登录授权抓取音频。
- 不做完整 ASR pipeline。
- 不做节拍、和声、频谱、音色等低层音频 DSP。
- 不做音乐推荐系统。
- 不把曲名推测成真实听感证据。

## 6. 契约设计

V6-B 输出仍复用 `InputFeature`：

```text
InputFeature
├── inputId
├── featureType = music
├── lowLevelFeatures
│   ├── musicParsingStatus
│   ├── sourceTextType
│   ├── moodTone 或 lyricalImagery
│   └── density / tempoImpression / atmosphere（仅在有证据时）
├── sampleEvidence
├── promptVersion
└── modelName
```

建议 feature key：

| key | 说明 | evidence 要求 |
| --- | --- | --- |
| `musicParsingStatus` | `metadata_only` / `lyrics_or_transcript_parsed` / `placeholder` / `failed` | 必须说明来源 |
| `sourceTextType` | `title` / `description` / `lyrics` / `transcript` / `notes` | 必须引用用户提供文本 |
| `lyricalImagery` | 歌词/文字中的意象类型 | 仅 lyrics/transcript/notes 可用 |
| `moodTone` | 文本证据支持的氛围词 | 不得写成人格判断 |
| `tempoImpression` | 用户笔记中明确提到快慢时可用 | 不从曲名猜测 |

## 7. API / 数据影响

首版建议不改数据库：

```text
music input 的 contentText / description 可承载用户主动提供的 lyrics / transcript / notes。
```

如果后续需要明确字段，可在 V6-B 后半段或 V6-D hardening 中评估：

```text
musicContentKind = title_only | notes | lyrics | transcript
```

首版不建议现在改 API，因为现有 `CreateInputRequest` 已支持：

- `type=music`
- `contentText`
- `title`
- `description`
- `fileUrl`

## 8. 失败语义

| 场景 | 处理 |
| --- | --- |
| `MUSIC_FEATURE_RUNTIME=metadata_only` 且只有 title/fileUrl | 成功，但 feature 标记 `metadata_only` |
| 用户提供 lyrics/transcript/notes | 成功，feature 标记 `lyrics_or_transcript_parsed` |
| `MUSIC_FEATURE_RUNTIME=disabled` 遇到 music input | fail-fast |
| `MUSIC_FEATURE_RUNTIME=asr_local` 后续启用但模型失败 | fail-fast 或 explicit `failed`，不得 silent fallback mock |
| metadata-only 输出试图生成“听见了鼓点/旋律/音色” | validator 拦截 |
| 输出人格/心理/能力/命运判断 | validator 拦截 |

## 9. 验收标准

### 9.1 自动验证

- [x] music metadata-only path 测试通过。
- [x] music text-notes / lyrics path 测试通过。
- [x] disabled path fail-fast 测试通过。
- [x] validator 拦截无证据 audio claim。
- [x] governance 测试确认不输出人格/心理/能力/命运式判断。
- [x] Debug `mockUsage` / boundary warning 标记 music runtime。
- [x] 后端全量 pytest 通过。

### 9.2 人工验证

- [ ] 创建只有 title 的 music input，报告/debug 不声称已听音频。
- [ ] 创建含歌词/笔记的 music input，报告可引用用户提供文本证据。
- [ ] 配置 disabled runtime，music 输入应失败而不是 silent fallback mock。
- [ ] 若未来部署 ASR/audio runtime，再补真实音频解析人工验收。

## 10. AI 生成顺序

1. 读取 V6-A factory / image extractor / validator 流程。
2. 新增 music runtime 配置。
3. 新增 `AudioMusicFeatureExtractor` mock / metadata_only / text_notes / disabled。
4. 将 factory 扩展为 image + music modality routing。
5. 增加 music feature validator。
6. 更新 Debug mockUsage / boundary warning。
7. 补充 unit / integration governance 测试。
8. 更新 `.env.example`、`启动说明.md`、`docs/13`、`docs/15`。

## 11. 用户确认（已接受，2026-06-23）

- [x] 接受 V6-B 首版不做完整 ASR / 低层音频 DSP。
- [x] 接受 `metadata_only` 是 music 的合法默认路径，但必须显性标记。
- [x] 接受用户提供 lyrics / transcript / notes 可以作为 text-derived music evidence。
- [x] 接受不抓取流媒体或版权音频内容。
- [x] 接受后续如接入真实 ASR/audio runtime，失败不得 silent fallback mock。
- [x] 接受 V6-B 完成后进入 V6-C Video Understanding Boundary。

## 12. 当前结论

```text
V6-B 已完成 metadata_only + text_notes + disabled + mock 边界实现，状态 ready_for_validation / accepted_auto。
自动验证：
- python -m pytest backend/app/tests/unit/test_v6b_audio_music_feature_runtime.py -q
  8 passed
- python -m pytest backend/app/tests/unit/test_feature_schema.py backend/app/tests/unit/test_v6a_image_feature_runtime.py backend/app/tests/unit/test_v6b_audio_music_feature_runtime.py backend/app/tests/integration/test_api_flow.py backend/app/tests/integration/test_v5e_governance_validation.py -q
  21 passed, 3 warnings
- python -m pytest backend/app/tests -q
  134 passed, 5 warnings

V6-B 首版不依赖真实 ASR/audio 模型；未来如部署真实 audio runtime，另行进入后续子阶段或 hardening 验收。
```

## 13. 本轮实现记录（2026-06-23）

- 新增 `MUSIC_FEATURE_RUNTIME=metadata_only|text_notes|mock|disabled`。
- 新增 `AudioMusicFeatureExtractor` 等价实现：metadata-only、text-notes、mock placeholder、disabled fail-fast。
- 扩展 default modality factory：image 走 V6-A runtime，music 走 V6-B runtime，text/video 保持既有 fallback。
- 新增 music feature governance validator：
  - metadata-only 不得声称听见鼓点、旋律、音色、节拍等真实音频内容；
  - 不得输出人格、心理、能力、命运式判断。
- Debug `mockUsage` / boundary warning 可显示 music runtime 边界。
- 更新 `backend/.env.example` 与 `backend/启动说明.md`。
