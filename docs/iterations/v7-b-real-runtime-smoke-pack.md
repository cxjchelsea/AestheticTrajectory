# V7-B：Real Runtime Smoke Pack

当前状态：

```text
ready_for_validation / accepted_auto
```

创建日期：

```text
2026-06-23
```

## 1. 本轮定位

V7-B 是 V7 的第二个子阶段，目标是把真实 runtime 的部署验证从“人工临时测试”整理成可重复执行的 smoke pack。

本轮目标：

```text
为 Ollama report runtime、Ollama vision runtime、Postgres、Chroma 等真实/外部 runtime 建立一组可选 smoke commands、验收 checklist 和失败记录模板。
```

V7-B 不是默认 CI 改造阶段：

```text
默认 pytest baseline 仍保持 memory/mock/metadata-only，不依赖外部服务。
真实 runtime smoke 是 optional / local / pre-release gate。
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v7-0-production-validation-graduation-roadmap-research.md`
2. `docs/iterations/v7-a-graduation-roadmap-acceptance-bar.md`
3. `docs/archive/v6/V6-遗留问题.md`
4. `docs/13-验证与评估文档.md`
5. `docs/20-多模态偏好建模设计文档.md`
6. `backend/启动说明.md`
7. `backend/.env.example`

## 3. 问题定义

V6 已完成真实 runtime 的 adapter 和治理边界，但仍存在：

```text
V6-A real vision validation pending
Postgres / Chroma / Ollama smoke 仍依赖人工记忆
真实 runtime 失败时缺少统一记录模板
```

V7-B 要把这些变成：

```text
可执行命令
可复核 checklist
可记录结果
不污染默认 CI
```

## 4. 系统边界

本阶段做：

- 整理 real runtime smoke scope。
- 明确哪些 smoke 必做、可选、环境 pending。
- 在文档中定义 smoke commands。
- 在验证文档中记录 smoke checklist。
- 如需要，新增轻量测试标记或说明，但不把外部服务纳入默认 pytest。

本阶段不做：

- 不强制用户立即部署多模态模型。
- 不把 Ollama / Postgres / Chroma smoke 加进默认 `python -m pytest backend/app/tests -q`。
- 不实现真实 audio/video parser。
- 不接 LangSmith / OTel / Sentry。
- 不修改业务 schema。

## 5. Smoke Pack 候选范围

| Runtime | V7-B 分类 | 验收方式 |
| --- | --- | --- |
| default pytest baseline | 必须保持 | `python -m pytest backend/app/tests -q` |
| Ollama report LLM | smoke 候选 | `REPORT_LLM_RUNTIME=ollama` 下生成报告 |
| Ollama vision image | smoke 候选 / 取决于模型 | `IMAGE_FEATURE_RUNTIME=ollama_vision` 下图片解析 |
| Postgres repository | smoke 候选 | alembic + API flow |
| Chroma vector write/query | smoke 候选 | `CHROMA_ENABLED=true` 下 write / debug trace |
| music/audio real runtime | 非 V7-B 默认 | 后续 V8/V9 决策 |
| video real runtime | 非 V7-B 默认 | 后续 V8/V9 决策 |

## 6. 验收标准

- [x] 默认 pytest baseline 仍保持无外部依赖。
- [x] smoke pack 明确哪些命令是 optional / local。
- [x] V6-A real vision validation 有可执行路径或明确保留 pending。
- [x] Postgres / Chroma / Ollama smoke 有 checklist。
- [x] smoke 失败记录模板包含 runtime、env、command、expected、actual、classification、next action。
- [x] `backend/启动说明.md` 和 `docs/13` 状态一致。
- [x] 不引入默认 CI 外部依赖。

## 7. 用户确认（已接受，2026-06-23）

- [x] 接受 V7-B 只建立 real runtime smoke pack，不强制外部服务进入默认 CI。
- [x] 接受如果当前没有 vision 模型，V6-A real vision validation 继续保留 pending。
- [x] 接受 V7-B 不实现真实 audio/video parser。
- [x] 接受 Postgres / Chroma / Ollama smoke 以 optional local commands 形式记录。
- [x] 接受 smoke 失败优先记录与分类，不用 mock fallback 掩盖。

## 8. AI 生成顺序

确认后建议按以下顺序执行：

1. 读取 `backend/启动说明.md`、`.env.example`、现有 V6 tests。
2. 整理 smoke pack scope 和命令。
3. 更新 `backend/启动说明.md`。
4. 更新 `docs/13-验证与评估文档.md`。
5. 如需要，新增 smoke result template 文档。
6. 同步 `docs/12`、`docs/15`、`docs/README.md`。

## 9. 当前结论

```text
V7-B 已完成 Real Runtime Smoke Pack，状态 ready_for_validation / accepted_auto。
本轮结果：
- `backend/启动说明.md` 已新增 V7-B smoke pack。
- `docs/13` 已同步 V7-B smoke 验收口径。
- 默认 pytest baseline 保持无外部依赖。
- V6-A real vision validation 在未部署模型时继续 pending。
- 未实现真实 audio/video parser。
```

## 10. 本轮实现记录（2026-06-23）

- 新增默认 baseline smoke：
  - `python -m pytest backend/app/tests -q`
- 新增 optional/local smoke checklist：
  - PostgreSQL repository。
  - Chroma vector runtime。
  - Ollama report LLM。
  - Ollama vision image。
- 新增 smoke 失败记录模板。
- 明确 smoke 失败不得 silent fallback mock。
- 本阶段只改文档，不改 runtime 代码。
