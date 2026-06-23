# V6-A：Image Understanding Runtime

当前状态：

```text
ready_for_validation / real_model_pending
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V6-A 目标：

```text
让 image 输入从“上传后 metadata/placeholder”升级为可追溯的视觉内容解析，产出结构化 InputFeature，并在 debug 中明确 real/mock/metadata-only runtime 边界。
```

V6-A 不追求完整视觉理解平台，而是先建立 image runtime 的最小可信链路。

## 2. 上游依据

必须引用：

1. `docs/iterations/v6-0-multimodal-runtime-production-hardening-research.md`
2. `docs/20-多模态偏好建模设计文档.md` §3.1-§3.5 / §7
3. `docs/10-Prompt Contract 与结构化输出规范.md`
4. `docs/13-验证与评估文档.md` §15.3 / §15.4
5. `backend/启动说明.md` §6（Ollama runtime）
6. V5-B report LLM runtime 实现与 validator

## 3. 问题定义

当前状态：

- image 可以通过 upload API 保存并生成 `fileUrl`。
- workflow 仍使用 mock/heuristic feature extraction。
- 报告不能诚实声称理解了图片内容。

V6-A 解决：

```text
当用户上传 image 文件时，系统能调用可替换的 image understanding runtime，生成结构化 InputFeature，并保留 evidence / promptVersion / modelName / debug boundary。
```

## 4. 方案选择（候选）

### 4.1 推荐路径

```text
ImageFeatureExtractor adapter
→ 读取本地 image bytes / file path
→ image caption / visual analysis prompt
→ 结构化 JSON
→ InputFeature validator
→ 进入既有 workflow
```

### 4.2 Runtime 候选

| Runtime | 用途 | V6-A 判断 |
| --- | --- | --- |
| `mock` | CI / dev baseline | 保留，必须 dev-only 标记 |
| `ollama_vision` | 本地视觉模型路径 | 可作为首选 real path，需确认可用模型 |
| `remote_vision` | 远程 vision API | 只做接口边界或后续扩展，不作为首版硬依赖 |

V6-A 默认建议：

```text
IMAGE_FEATURE_RUNTIME=mock|ollama_vision
IMAGE_FEATURE_MODEL=...
```

当前本机暂无可用 vision 模型。V6-A 先实现 adapter / schema / mock / disabled / ollama_vision 占位路径，
自动验收不依赖真实 vision 服务；真实模型部署后的完整人工验收后置记录为 pending_validation。

## 5. 系统边界

### 5.1 必做

- [x] 新增 image feature runtime 配置。
- [x] 新增 `ImageFeatureExtractor` 或等价 adapter 协议。
- [x] 保留 mock image extractor 作为 CI/dev path，并在 debug 中标记 dev-only。
- [x] 实现真实 image runtime 的最小路径或明确 disabled fail-fast。
- [x] 输出必须是 `InputFeature`，包含 evidence、promptVersion、modelName。
- [x] image runtime 输出必须经过 schema / governance validation。
- [x] Debug 中能看出 image parsed / metadata-only / mock / failed。
- [x] 测试覆盖：mock path、disabled/fail-fast path、schema invalid path、governance 禁句。
- [x] 更新 `backend/.env.example`、`backend/启动说明.md`、必要文档。

### 5.2 不做

- [ ] 不做人脸身份识别。
- [ ] 不做 OCR 全量能力。
- [ ] 不做图像生成。
- [ ] 不做完整相册/批量视觉检索平台。
- [ ] 不把 image feature 直接写 profile positive evidence。
- [ ] 不在真实 runtime 失败时 silent fallback mock。

## 6. 契约设计

### 6.1 InputFeature 输出约束

V6-A image extractor 输出仍使用：

```text
InputFeature
├── inputId
├── featureType = image
├── lowLevelFeatures
├── sampleEvidence
├── promptVersion
└── modelName
```

建议 image low-level feature keys：

```text
color_temperature
saturation
density
composition
material
presence
lighting
space
```

### 6.2 失败语义

| 场景 | 预期 |
| --- | --- |
| `IMAGE_FEATURE_RUNTIME=mock` | workflow 可完成；debug 标记 mock/dev-only |
| `IMAGE_FEATURE_RUNTIME=disabled` 且输入含 image | fail-fast 或明确 placeholder，不声称 image parsed |
| real runtime 连接失败 | fail-fast，不 silent fallback mock |
| real runtime 返回 invalid JSON | fail-fast，记录 schema validation failed |
| image 文件缺失 | 4xx/5xx fail-fast，不伪造 feature |

## 7. API / UI 影响

后端：

- 可能新增 image runtime config。
- 可能扩展 `MockUsageRecord` 或 boundary warning 文案。
- 不新增 public API path；仍通过现有 `/api/inputs` + `/api/analysis-jobs`。

前端：

- 上传页不需要大改。
- 报告页 evidence 展示沿用现有 `EvidenceList`。
- Debug 面板如已有 boundary/mock 信息可复用；必要时只补文案。

## 8. 验收标准

### 8.1 自动验证

- [x] image mock path 测试通过。
- [x] image real/disabled runtime fail-fast 测试通过。
- [x] invalid image LLM output 被 validator 拦截。
- [x] governance 测试确认不输出人格/心理/能力/命运式判断。
- [x] 后端全量 pytest 通过。
- [x] 前端未改动，未运行 frontend build。

### 8.2 人工验证

- [ ] 上传至少 3 张 image 或 image + text 混合输入。
- [ ] 运行分析，报告能引用 image input evidence。
- [ ] Debug 中可见 image runtime 的 mock/real/metadata-only 边界。
- [ ] 如果配置真实 vision 模型，报告内容应能反映图片可见结构，而不是只读 title。
- [ ] 关闭/错误配置真实 vision runtime 时，系统不得 silent fallback mock。

说明：

```text
当前无可用 vision 模型；本轮已完成自动验收，真实模型部署后再做完整人工验收。
```

## 9. AI 生成顺序

1. 读取现有 `extract_features`、feature schema、mock extractor。
2. 设计 image extractor protocol / factory。
3. 增加 config 与 mock/disabled/real adapter。
4. 接入 workflow step。
5. 增加 validator / governance tests。
6. 更新 Debug boundary/mock usage。
7. 跑 V6-A 定向测试与后端全量 pytest。
8. 更新 docs/15、docs/12、README、启动说明。

## 10. 用户确认（已接受，2026-06-23）

- [x] 接受 V6-A 首版目标是 image understanding runtime，不做 audio/video。
- [x] 接受 V6-A 不做人脸身份识别、OCR 全量、图像生成。
- [x] 接受真实 image runtime 失败 fail-fast，不 silent fallback mock。
- [x] 接受如果本机暂无 vision 模型，先完成 adapter/mock/disabled 边界，再人工配置真实模型验收。
- [x] 接受 V6-A 完成后进入 V6-B Audio / Music Understanding Boundary。

## 11. 当前结论

```text
V6-A 已完成 adapter/mock/disabled/ollama_vision 占位实现与自动治理测试，状态 ready_for_validation / real_model_pending。
自动验证：
- python -m pytest backend/app/tests/unit/test_v6a_image_feature_runtime.py -q
  6 passed
- python -m pytest backend/app/tests/unit/test_feature_schema.py backend/app/tests/integration/test_api_flow.py backend/app/tests/integration/test_v5e_governance_validation.py backend/app/tests/unit/test_v6a_image_feature_runtime.py -q
  13 passed, 3 warnings
- python -m pytest backend/app/tests -q
  126 passed, 5 warnings

真实 vision 模型尚未部署；完整人工验收待模型部署后执行。
```

## 12. 本轮实现记录（2026-06-23）

- 新增 `IMAGE_FEATURE_RUNTIME=mock|disabled|ollama_vision`、`IMAGE_FEATURE_MODEL`、`IMAGE_FEATURE_TIMEOUT_SECONDS`。
- 新增 image feature extractor：mock placeholder、disabled fail-fast、Ollama vision JSON adapter。
- 默认 `extract_features` 通过 factory 选择 modality extractor，image 走 V6-A runtime，text/music/video 暂沿用 mock feature extractor。
- 新增 image feature governance validator，阻止人格/心理/能力/命运式输出。
- Debug `mockUsage` / boundary warning 可显示 image runtime 的 mock/real/disabled 状态。
- 更新 `backend/.env.example` 与 `backend/启动说明.md`。
