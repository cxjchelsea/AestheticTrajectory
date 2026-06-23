# V6-D：Production Hardening & Runtime CI

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V6-D 目标：

```text
把 V5/V6-A/B/C 留下的生产集成债务收束到测试隔离、配置一致性、warning 策略、runtime smoke 分层和 debug boundary 上。
```

V6-D 不新增新模态能力，而是让当前多模态 runtime baseline 更适合持续开发和后续真实模型接入。

## 2. 上游依据

必须引用：

1. `docs/iterations/v6-0-multimodal-runtime-production-hardening-research.md`
2. V6-A / V6-B / V6-C 三个 modality runtime 任务单
3. `docs/13-验证与评估文档.md` §15.3 / §15.4
4. `backend/启动说明.md`
5. 当前后端测试结果：`142 passed, 5 warnings`
6. V5-D 对 Pydantic/FastAPI alias warning 的 non-blocking tech-debt 结论

## 3. 问题定义

当前状态：

- V6-A/B/C 已实现 image/music/video 的 mock/metadata-only/text-notes/disabled/real-placeholder 边界。
- 后端全量 pytest 通过，但仍有 5 条 Pydantic/FastAPI alias warning。
- 测试默认 memory backend，但部分 integration / upload 测试会生成本地 `uploads/` 临时文件。
- 真实 runtime smoke 与 CI memory path 还没有明确分层。
- `.env.example`、`启动说明.md`、debug mockUsage / boundary warning 已扩展，但缺少一次硬化验收。

V6-D 解决：

```text
明确哪些 warning 必须修，哪些作为已知框架 warning 管理；
明确 CI 默认路径不依赖真实模型 / Chroma / Postgres；
明确 real runtime smoke 是本地人工或可选测试，不阻塞默认 pytest；
补齐测试隔离、配置一致性和 debug boundary 的自动检查。
```

## 4. 方案选择

### 4.1 Warning 策略

候选：

| 方案 | 优点 | 风险 | 判断 |
| --- | --- | --- | --- |
| 立即重构所有 Pydantic alias 字段 | 警告可能清零 | 容易改变 API JSON 契约，V5-D 已试过收益不稳定 | 不推荐直接大改 |
| 升级 FastAPI / Pydantic | 可能从根源解决 | 版本升级影响面大，需要独立验证 | 可作为 spike |
| 将已知 warning 纳入 pytest 过滤/文档 | CI 更干净 | 可能掩盖新增 warning | 可做，但必须精确匹配 |
| 保持 warning 但加守护测试/记录 | 不改 API 契约 | 输出仍不干净 | 当前基线 |

V6-D 推荐：

```text
先做 warning inventory + precise filter 可行性；
只有在不改变 API JSON 字段契约的前提下，才清理或过滤。
```

### 4.2 测试隔离策略

推荐：

```text
默认 pytest：memory backend + mock/metadata-only runtimes，无外部依赖
可选 smoke：Postgres / Chroma / Ollama / real image runtime，本地人工触发
```

V6-D 不要求 Windows 本机必须引入 testcontainers，但需要给出可行性结论：

- 当前是否适合引入 Docker / testcontainers。
- 如果不引入，如何保证 memory / database 两层测试职责清晰。
- 本地 `uploads/` 测试产物如何隔离或清理。

### 4.3 Runtime smoke 分层

默认 CI 不应依赖：

- Ollama。
- Chroma。
- PostgreSQL 本地实例。
- vision/audio/video 真实模型。
- 外部 OAuth provider。

可选 smoke 建议分层：

```text
SMOKE_POSTGRES=true
SMOKE_CHROMA=true
SMOKE_OLLAMA=true
SMOKE_IMAGE_RUNTIME=true
```

是否新增这些 env / marker 由 V6-D 实现阶段决定。

## 5. 系统边界

### 5.1 本轮包含

- 盘点并处理 Pydantic/FastAPI alias warning 策略。
- 明确默认 pytest 与 optional smoke 的分层。
- 评估 clean DB fixture / testcontainers 是否纳入当前项目。
- 检查 upload 测试产物隔离或清理策略。
- 增加必要的 config / debug boundary 一致性测试。
- 更新 `.env.example`、`启动说明.md`、`docs/13`。

### 5.2 本轮不做

- 不接入真实 LangSmith / OTel / Sentry 生产观测平台。
- 不强制部署 Postgres / Chroma / Ollama / vision/audio/video 模型。
- 不把 mock/metadata-only runtime 改成真实 runtime。
- 不做 V6 final archive。
- 不大规模重构 API schema，除非能证明不改变现有 JSON 契约。

## 6. 候选实现项

优先级建议：

1. `pytest` warning inventory：确认 5 条 warning 来源、触发测试、字段名。
2. Pydantic alias warning 处理决策：
   - 精确过滤已知 warning；
   - 或记录为 explicit known warning baseline；
   - 或小范围升级/修复 spike。
3. 测试上传目录隔离：
   - 使用临时 `UPLOAD_DIR`；
   - 或 fixture 自动清理测试文件。
4. Runtime smoke marker：
   - 将外部依赖测试显式标记；
   - 默认测试不触发外部服务。
5. Config consistency test：
   - `.env.example` 包含 V6-A/B/C runtime env；
   - `settings` 读取默认值一致。
6. Debug boundary consistency test：
   - image/music/video mockUsage 和 boundary warning 不互相覆盖。

## 7. 验收标准

### 7.1 自动验证

- [x] 后端全量 pytest 通过。
- [x] warning 策略明确：清零、精确过滤或 documented baseline 三选一。
- [x] 不改变现有 API JSON 字段契约。
- [x] 默认 pytest 不依赖 Postgres / Chroma / Ollama / real multimodal model。
- [x] 上传测试产物不污染根目录 `uploads/`。
- [x] `.env.example` 与 `settings` 默认值一致。
- [x] Debug boundary 对 image/music/video runtime 状态有测试覆盖。

### 7.2 人工验证

- [ ] 按 `backend/启动说明.md` 跑默认 memory backend。
- [ ] 按需跑 Postgres / Chroma / Ollama optional smoke。
- [ ] 确认 V6-A real vision pending validation 不阻塞默认测试。

## 8. AI 生成顺序

1. 运行 warning inventory，定位 5 条 warning 来源。
2. 检查 upload 测试产物来源和 `UPLOAD_DIR` fixture。
3. 检查 `.env.example` 与 `settings` 默认值一致性。
4. 检查 debug mockUsage / boundary 对 image/music/video 的测试覆盖。
5. 决策 warning 策略并实现最小改动。
6. 补充测试。
7. 运行全量 pytest。
8. 更新 `docs/13`、`docs/15`、`backend/启动说明.md`。

## 9. 用户确认（已接受，2026-06-23）

- [x] 接受 V6-D 不新增新模态能力，只做 production hardening / runtime CI。
- [x] 接受 Pydantic/FastAPI alias warning 以“不改变 API JSON 契约”为最高优先级。
- [x] 接受默认 pytest 不依赖 Postgres / Chroma / Ollama / 真实多模态模型。
- [x] 接受真实 runtime smoke 作为 optional / local path，不阻塞 CI baseline。
- [x] 接受 testcontainers 先做可行性判断，不强制引入。
- [x] 接受 V6-D 完成后进入 V6-E Multimodal Governance Validation & Closure Prep。

## 10. 当前结论

```text
V6-D 已完成首版 production hardening / runtime CI，状态 ready_for_validation / accepted_auto。
本轮结果：
- Pydantic/FastAPI alias warning：保留 API JSON 契约不变，使用 pytest 精确 message filter 管理已知 compatibility warning。
- 默认 pytest：memory backend + mock/metadata-only runtimes，无 Postgres / Chroma / Ollama / real multimodal model 依赖。
- 上传隔离：测试默认 `UPLOAD_DIR` 指向 pytest tmp dir，不污染项目根目录 `uploads/`。
- Config consistency：`.env.example` 与 `settings` 默认值有测试覆盖。
- Debug boundary：image/music/video runtime 状态有测试覆盖。

自动验证：
- python -m pytest backend/app/tests/unit/test_v6d_runtime_hardening.py backend/app/tests/integration/test_v6d_upload_isolation.py -q
  4 passed
- python -m pytest backend/app/tests/unit/test_v6d_runtime_hardening.py backend/app/tests/integration/test_v6d_upload_isolation.py backend/app/tests/unit/test_v6a_image_feature_runtime.py backend/app/tests/unit/test_v6b_audio_music_feature_runtime.py backend/app/tests/unit/test_v6c_video_feature_runtime.py backend/app/tests/integration/test_api_flow.py backend/app/tests/integration/test_v5e_governance_validation.py -q
  30 passed
- python -m pytest backend/app/tests -q
  146 passed
```

## 11. 本轮实现记录（2026-06-23）

- 在 `backend/pyproject.toml` 中对已知 Pydantic/FastAPI alias compatibility warning 增加精确 message filter。
- 扩展测试 fixture：默认 runtime 使用 memory/mock/metadata-only，并将 `UPLOAD_DIR` 指向 pytest 临时目录。
- 新增 V6-D hardening 测试：
  - `.env.example` 与 `settings` 默认值一致；
  - 默认 pytest runtime 不依赖外部服务；
  - debug boundary 覆盖 image/music/video runtime；
  - upload API 不污染项目根目录 `uploads/`。
- 保持现有 API JSON 字段契约不变；不做 schema 大规模重构。
