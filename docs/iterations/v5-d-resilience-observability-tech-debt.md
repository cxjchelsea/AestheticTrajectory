# V5-D：Resilience, Observability & Tech-debt

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-23
```

## 1. 本轮目标

V5-D 目标：

```text
对齐 V5 真实 runtime 之后的降级语义和可观测性边界，优先修复 Chroma / knowledge 不可达导致核心 workflow 500 的问题，
同时清理已知测试与 Pydantic/FastAPI alias warning tech-debt，为 V5-E 全链路治理验收做准备。
```

V5-D 不是新功能扩张阶段，而是把 V5-A/B/C 引入的真实身份、真实 LLM、真实外部源边界变成可维护、可追踪、可回归的运行时。

## 2. 上游依据

必须引用：

1. `docs/iterations/v5-0-production-runtime-trust-boundary-research.md` §6 / §7 / §8 / §10
2. `docs/iterations/v5-a-identity-access-boundary.md`
3. `docs/iterations/v5-b-real-report-runtime.md`
4. `docs/iterations/v5-c-production-mcp-oauth.md`
5. `docs/archive/v4/V4-遗留问题.md` §5
6. `docs/02-版本迭代路线图.md` §11 / §14
7. `docs/12-开发任务拆分与里程碑计划.md` §2 / §8
8. `docs/13-验证与评估文档.md`
9. `docs/15-迭代执行记录.md` §29

## 3. 问题定义

V5-A/B/C 已解决：

- 持久匿名 session 与 API user scope。
- Ollama report LLM 生成 interpretations / insights。
- mock_oauth external source → preview → confirm import。

V5-D 解决：

```text
当非核心增强能力不可达时，核心分析流程是否仍能完成，并且降级原因是否能被 debug / fallback trace 看见？
```

当前已知问题：

| 问题 | 当前表现 | V5-D 目标 |
| --- | --- | --- |
| Knowledge vector store 不可达 | `retrieve_aesthetic_knowledge` 可能随 Chroma 初始化/query 失败而中断 workflow | 与 `write_vectors` 一样 graceful degrade |
| Chroma write vs knowledge query 降级不一致 | write_vectors 有 `ChromaWriteResult`，knowledge 仅返回 context | 增加 retrieval path / fallback event / boundary warning |
| Pydantic alias warnings | pytest 通过但有 5 条 warning | 若契约风险低，记录并最小修复；若涉及 schema，优先修复 |
| DB integration fixture | 当前依赖 memory + 本机 database smoke | 记录干净 DB 策略；不强制 testcontainers |
| OTel / LangSmith | 历史多次 deferred | 明确 dev-only / optional，不作为 V5-D 硬门槛 |

## 4. 当前实现快照（V5-D 起点）

| 模块 | 当前状态 |
| --- | --- |
| `write_vectors` | 捕获 Chroma exception，返回 `ChromaWriteResult(status=failed)`，workflow 继续 |
| `_chroma_fallback_events` | 已把 write_vectors skipped/failed 转为 fallback event |
| `_chroma_boundary_status` | Debug 中有 ChromaDB runtime writes 边界 |
| `retrieve_aesthetic_knowledge` | 直接调用 `get_knowledge_vector_store()` 和 `build_aesthetic_knowledge_context()` |
| `KnowledgeVectorStore` | `ensure_seeded()` / `query()` 无局部 exception 转换 |
| `build_aesthetic_knowledge_context` | 已有 graph/vector retrieval trace 语义，但依赖 vector store 可用 |
| Tests | pytest 113 passed，仍有 Pydantic alias warnings |
| Frontend | Developer Debug 展示 workflow/fallback/mock/schema/boundary/retrieval |

## 5. 方案调研与选择

### 5.1 调研问题

| 问题 | 结论 |
| --- | --- |
| Chroma knowledge 失败是否 fail-fast？ | 否。Knowledge / RAG 是增强上下文，不应阻断 core report |
| LLM report 失败是否 graceful degrade？ | 否。V5-B 已确认 real LLM runtime schema/validator 失败应 fail-fast |
| DB 不可达是否 graceful degrade？ | 否。业务存储属于核心事实，仍 fail-fast |
| OTel / LangSmith 是否接入？ | V5-D 可选 spike / boundary doc；不作为实现硬门槛 |
| Pydantic alias warnings 是否必须全清？ | 若影响 API schema 或前后端契约则清；否则记录到 V5-E/V6 tech-debt |

### 5.2 方案对比

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 在 `retrieve_aesthetic_knowledge` 捕获异常并返回 abstained context | 改动小，符合增强能力降级 | 需要记录 fallback reason | **采用** |
| B 在 vector store 层吞异常 | 局部封装 | 容易隐藏错误来源 | 仅作为辅助，不作为唯一层 |
| C Chroma 不可达时关闭所有 retrieval | 稳定 | 损失 graph retrieval | 拒绝，graph 可继续 |
| D 接入完整 OTel/LangSmith | 运维能力强 | 超 V5-D 主目标 | 可选，不阻塞 |
| E testcontainers 干净 DB | 最可靠 | Windows/Docker 当前不稳定 | deferred，记录替代方案 |

## 6. 系统边界

### 6.1 必做

- [x] `retrieve_aesthetic_knowledge` 在 vector store init / seed / query 失败时不让 workflow 500。
- [x] 增加显性 fallback event：`knowledge_vector_retrieval_failed`。
- [x] Debug `Boundary Warnings` 明示 knowledge vector path degraded。
- [x] 保留 tag / graph retrieval 路径，不因 vector failure 全部 abstain。
- [x] 测试：vector store init/query 不可达时 knowledge context graceful degrade。
- [x] 测试：fallback event / retrieval trace 能看到降级原因。
- [x] 当前 Pydantic alias warnings 已定位为 FastAPI/Pydantic 兼容噪声；保留为 non-blocking tech-debt。
- [x] 文档化 database integration test 策略：本机 database smoke + CI memory；testcontainers deferred。

### 6.2 可选

- [ ] 最小 OTel / LangSmith boundary spike：只记录配置与 debug boundary，不接生产 exporter。
- [ ] 对 V5-C token storage 增加 dev-only warning / debug redaction 测试。

### 6.3 不做

- [ ] 不做复杂 observability dashboard。
- [ ] 不做 LLM-as-judge evaluation。
- [ ] 不做生产级 OTel collector / LangSmith SaaS 强依赖。
- [ ] 不做 Docker/testcontainers 硬依赖。
- [ ] 不把 LLM report runtime 错误 silent fallback 到 mock。
- [ ] 不把 database 不可达降级为 memory。

## 7. 契约设计

### 7.1 降级等级

| 能力 | 类型 | 失败语义 |
| --- | --- | --- |
| PostgreSQL repository | 核心事实 | fail-fast |
| input/report/profile/timeline APIs | 核心事实 | fail-fast / 4xx / 5xx |
| Report LLM real runtime | Level 0 生成核心 | fail-fast |
| Chroma `write_vectors` | 增强索引 | graceful degrade + fallback event |
| Knowledge vector query | 增强上下文 | graceful degrade + fallback event |
| Knowledge graph query | 增强上下文 | 尽量保留；失败才局部降级 |
| External source preview | 用户触发增强 | fail-fast 给用户，不影响历史 confirmed context |

### 7.2 Fallback event 候选

```json
{
  "fallbackType": "knowledge_vector_retrieval_failed",
  "fallbackAction": "Continued report generation with graph/static knowledge only",
  "severity": "warning",
  "userVisible": false
}
```

### 7.3 Retrieval trace 候选

```text
retrievalType = aesthetic_knowledge
status = degraded | abstained | success
vectorPath = failed | skipped | used
developerMessage = Chroma knowledge vector query failed: ...
```

## 8. API / UI 影响

后端：

- `AnalysisJobDebugResponse` 结构尽量不新增字段；优先复用 `fallbackEvents`、`boundaryWarnings`、`retrievalTrace`。
- 如需新增 `FallbackEvent.stepId=retrieve_aesthetic_knowledge`，前端已可展示。

前端：

- Developer Debug 已展示 fallback/boundary/retrieval；V5-D 首版不新增复杂 UI。
- 若 retrieval trace developerMessage 太长，可在已有 `<small>` 展示中截断或保持原样。

## 9. 验收标准

### 9.1 自动验证

- [x] `CHROMA_ENABLED=false`：全量 pytest 通过。
- [x] `CHROMA_ENABLED=true` 且 vector store init/query 不可达：knowledge retrieval graceful degrade，不因 vector failure 500。
- [x] Debug 有 fallback event / boundary warning / retrieval trace 显示 knowledge vector degraded。
- [x] V5-A identity scope 测试仍通过。
- [x] V5-B report LLM validator / mock default 测试仍通过。
- [x] V5-C external source tests 仍通过。
- [x] Pydantic alias warnings 已记录为 non-blocking。

### 9.2 人工验证

- [x] 开启 `CHROMA_ENABLED=true`，不启动 Chroma。
- [x] 跑一次分析，报告能完成。
- [x] Developer Debug 中可见 Chroma / knowledge 降级信息。
- [x] 报告文案不暗示 RAG 一定成功；仍有 uncertainty / disclaimer。

人工验证记录：

```text
2026-06-23：用户确认 V5-D 人工验证成功。
```

### 9.3 安全 / 治理验收

- 降级不得伪造外部知识命中。
- 降级不得把 mock / placeholder 说成真实 retrieval。
- LLM 不可达仍按 V5-B fail-fast，不回退 mock。
- Database 不可达仍失败，不自动切 memory。

## 10. AI 生成代码顺序（候选）

1. 梳理 `retrieve_aesthetic_knowledge` / `build_aesthetic_knowledge_context` 返回契约。
2. 增加 knowledge retrieval 降级 result / fallback 表达。
3. Wire workflow / analysis_job_service fallback events。
4. 更新 Debug boundary warning / retrieval trace。
5. 增加 Chroma unavailable 测试。
6. 清理或记录 Pydantic alias warnings。
7. 跑 `pytest -q` 和前端 build（如前端改动）。
8. 更新 docs/12、docs/15、README、必要时 docs/13。

## 11. 用户确认（已接受，2026-06-23）

- [x] 接受 V5-D 主范围：**knowledge vector / Chroma 不可达时 graceful degrade + debug 可见**。
- [x] 接受 LLM report real runtime 仍 **fail-fast**，不 silent fallback mock。
- [x] 接受 database 不可达仍 fail-fast，不自动切 memory。
- [x] 接受 OTel / LangSmith 仅作为可选边界记录，不接生产 exporter。
- [x] 接受 testcontainers / Docker 干净 DB fixture 暂缓，记录本机 database smoke + CI memory 策略。
- [x] 接受 Pydantic alias warnings 优先修复；若风险低，可记录为 V5-E/V6 non-blocking。
- [x] 接受 V5-D 完成后进入 V5-E Governance Validation & Closure Prep。

## 12. 权威设计文档更新判断

V5-D 确认后、实现前建议：

- `docs/13`：新增 resilience / degradation 验证项。
- `docs/11`：如新增 retrieval fallback contract，补充 workflow/debug 契约。
- `docs/07`：本轮不新增持久表时不更新。

本任务单草案阶段暂不修改权威正文。

## 13. 当前结论

```text
V5-D 已完成实现与人工验收，状态 accepted / manual_validation_passed。
后端全量 pytest：117 passed, 5 warnings。
5 条 Pydantic alias warning 已定位为 FastAPI/Pydantic 兼容噪声；不改变当前 API 契约，记录为 V5-E/V6 non-blocking tech-debt。
前端未改动，未运行 frontend build。
```

## 14. 本轮实现记录（2026-06-23）

- `KnowledgeRetrievalMeta.vectorPath` 增加 `failed`，并记录 `vectorErrorMessage`。
- `build_aesthetic_knowledge_context` 捕获 vector seed/query 异常，保留 tag/graph-backed knowledge context。
- `retrieve_aesthetic_knowledge` 捕获 vector store 初始化异常，降级为无 vector rerank 的 knowledge context。
- Debug 新增 `knowledge_vector_retrieval_failed` fallback event；retrieval trace 在 vector failure 时显示 `status=degraded`、`vectorPath=failed`。
- Boundary warning 在 knowledge vector failure 时显示 RAG degraded。
- 新增 `test_v5d_resilience.py`，扩展 `test_observability_trace.py`。
