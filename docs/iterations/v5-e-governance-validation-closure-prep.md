# V5-E：Governance Validation & Closure Prep

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V5-E 是 V5 final closure 之前的治理验收轮，不是新功能扩张阶段。

目标：

```text
对 V5-A/B/C/D 引入的 identity、real LLM report runtime、external source OAuth、resilience/debug 边界做横切回归，
形成 test_v5e_governance_validation + 人工全链路验收清单，为后续 V5 archive gate 准备证据。
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v5-0-production-runtime-trust-boundary-research.md` §8 / §9 / §10
2. `docs/iterations/v5-a-identity-access-boundary.md`
3. `docs/iterations/v5-b-real-report-runtime.md`
4. `docs/iterations/v5-c-production-mcp-oauth.md`
5. `docs/iterations/v5-d-resilience-observability-tech-debt.md`
6. `docs/13-验证与评估文档.md` §15.3 / §15.4
7. `docs/15-迭代执行记录.md` §26-§30

## 3. 问题定义

V5-A/B/C/D 分别已经实现并人工验收：

- V5-A：持久匿名 session、API 对象级 user scope。
- V5-B：Ollama report LLM runtime、结构化 JSON、schema/governance validator、evidenceRefs。
- V5-C：mock_oauth external source、preview/confirm/reject、用户 scope。
- V5-D：knowledge vector / Chroma 不可达 graceful degrade + debug 可见。

V5-E 需要回答：

```text
这些能力合在一起运行时，是否仍满足 V1-V4 治理不变量和 V5 trust boundary？
```

## 4. 系统边界

### 4.1 必做

- [x] 新增 `test_v5e_governance_validation.py` 横切测试文件。
- [x] 覆盖 identity scope：跨 user 不可读取 report/job/debug/profile/external import。
- [x] 覆盖 real LLM/mock boundary：`mock` 路径必须标记 dev-only；`ollama` 边界由 V5-B 既有测试覆盖。
- [x] 覆盖 evidence governance：insight `evidenceRefs` 只引用当前 report inputs，不引用 external source 或 profile item 作为直接证据。
- [x] 覆盖 external source governance：只读、需确认、confirmed context 仍是 supplementary，不直接写 profile positive evidence。
- [x] 覆盖 resilience governance：knowledge vector failure 可 degrade；database / report LLM / schema validation 仍 fail-fast（V5-B/V5-D 测试覆盖）。
- [x] 覆盖 debug visibility：`authContext`、`mockUsage`、`boundaryWarnings`、`retrievalTrace` 保留核心信号。
- [x] 形成 V5 人工全链路验收清单。
- [x] 更新 docs/13、docs/15、docs/12、README 的 V5-E 状态与验收记录。

### 4.2 不做

- [ ] 不做 V5 archive 本身；archive gate 单独执行。
- [ ] 不新增生产 OAuth provider。
- [ ] 不新增 LLM provider。
- [ ] 不重构整个 debug panel。
- [ ] 不把 Pydantic/FastAPI alias warning 当作 V5-E blocking，除非出现实际 schema 契约问题。

## 5. 验收标准

### 5.1 自动验证

- [x] `python -m pytest backend/app/tests -q` 通过。
- [x] 新增 V5-E governance tests 通过。
- [x] V5-A/B/C/D 既有测试继续通过。
- [x] 前端未改动，未运行 frontend build。

### 5.2 人工验证

- [x] anonymous session 正常建立；刷新后同一用户可继续访问自己的报告。
- [x] 第二个 session/user 不能访问第一个用户的 job/report/debug/external import。
- [x] Ollama runtime 下报告为真实 LLM 生成，debug 不显示 mock interpretation enabled。
- [x] External source preview 必须确认后才进入 confirmed import。
- [x] Chroma 不可达时报告仍可完成，debug 可见 knowledge vector degradation。
- [x] 报告、观察、profile 页面不输出人格诊断、心理评估、能力判断或命运式表达。

人工验证记录：

```text
2026-06-23：用户确认 V5-E 人工验收通过。
```

### 5.3 安全 / 治理不变量

- [ ] 不伪造 evidence。
- [ ] 不把 external source 当作用户偏好事实。
- [ ] 不把 mock/dev-only 能力描述为生产真实能力。
- [ ] 不把核心存储错误降级为 memory。
- [ ] 不把 real LLM 失败 silent fallback 到 mock。

## 6. AI 生成顺序

1. 梳理 V5-A/B/C/D 已有 governance tests。
2. 新增 V5-E 横切测试，先覆盖最小不变量。
3. 根据测试暴露的问题修复代码或文档，不新增功能 scope。
4. 运行后端全量 pytest。
5. 如涉及前端，运行 frontend build。
6. 更新 V5-E 任务单、docs/13、docs/15、docs/12、README。
7. 提交用户人工验收清单。

## 7. 用户确认（已接受，2026-06-23）

- [x] 接受 V5-E 只做治理回归与 closure prep，不做 V5 archive 本身。
- [x] 接受 V5-E 不新增 provider / OAuth source / debug dashboard。
- [x] 接受 Pydantic alias warnings 若仍为兼容噪声，则继续记录为 V5 final closure tech-debt，不阻塞 V5-E。
- [x] 接受 V5-E 完成后进入 V5 final closure / archive gate。

## 8. 当前结论

```text
V5-E 已完成自动化治理回归与人工验收，状态 accepted / manual_validation_passed。
新增 V5-E governance tests：3 passed, 3 warnings。
V5-A/B/C/D/E 聚焦回归：18 passed, 3 warnings。
后端全量 pytest：120 passed, 5 warnings。
前端未改动，未运行 frontend build。
下一步进入 V5 final closure / archive gate。
```

## 9. 本轮实现记录（2026-06-23）

- 新增 `backend/app/tests/integration/test_v5e_governance_validation.py`。
- 覆盖跨用户访问 `report/evaluation/grouping-stability/job/debug/failure-replay/profile/reports/external-imports` 均返回 403。
- 覆盖 Debug `authContext`、`mockUsage`、`boundaryWarnings`、`retrievalTrace` 核心信号。
- 覆盖 report insight `evidenceRefs` 只引用当前 report inputs。
- 覆盖 mock insight 不出现诊断式治理禁句。
- 覆盖 external source preview/confirm 后仍不直接生成 profile positive evidence。
- Pydantic/FastAPI alias warning 仍为 5 条兼容噪声，继续作为 non-blocking tech-debt。
