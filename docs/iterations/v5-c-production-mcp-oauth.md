# V5-C：Production MCP OAuth

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-22
```

## 1. 本轮目标

V5-C 目标：

```text
在 V4-D mock external import + confirm 治理之上，接入最小生产级 OAuth MCP 只读外部源，
让用户可显式连接、拉取候选外部上下文、确认后导入 external_context_items。
```

本轮不是要做完整外部数据平台，而是验证：

```text
真实外部源是否能在 V5-A user scope、V5-B real LLM 边界已成立的前提下，
安全地成为 supplementary context，且不破坏 evidence-first / non-diagnostic / profile governance。
```

## 2. 上游依据

必须引用：

1. `docs/iterations/v5-0-production-runtime-trust-boundary-research.md` §7–§13
2. `docs/iterations/v5-a-identity-access-boundary.md`
3. `docs/iterations/v5-b-real-report-runtime.md`
4. `docs/iterations/v4-d-agent-runtime-mcp-integration.md`
5. `docs/02-版本迭代路线图.md` §11 / §14
6. `docs/12-开发任务拆分与里程碑计划.md` §2 / §8
7. `docs/13-验证与评估文档.md`
8. `docs/15-迭代执行记录.md` §23 / §27 / §28

外部规范参考：

- Model Context Protocol Authorization：OAuth 2.1、PKCE、Authorization Server Metadata、Protected Resource Metadata、Resource Indicators。

## 3. 问题定义

V4-D 已有：

- `external_import_batches`
- `external_context_items`
- `POST /api/users/{user_id}/external-imports`
- `confirm` / `reject`
- Agent observation 只把 confirmed external context 作为 supplementary context

但 V4-D 的外部导入来源仍是 in-app mock payload，不是真实授权源。

V5-C 解决的问题：

```text
如何把外部只读来源接入生产 OAuth 流程，同时保持用户确认、对象级 scope、审计和治理不变量？
```

不解决的问题：

- 不做后台定时同步。
- 不做 external write。
- 不把 external context 自动写入 profile positive evidence。
- 不做多 SaaS 集成平台或 connector marketplace。
- 不做企业 IAM / SSO。
- 不让 Agent 自主连接外部账号。

## 4. 当前实现快照（V5-C 起点）

| 能力 | 当前状态 |
| --- | --- |
| User scope | V5-A 已完成，API 对象级隔离已验收 |
| Report LLM | V5-B 已完成，Ollama insights / interpretations 已验收 |
| External import | V4-D mock import batch + confirm/reject 已完成 |
| External context storage | `external_import_batches` / `external_context_items` 已存在 |
| Agent observation | 可读取 confirmed external context，但不写 profile positive evidence |
| MCP stdio | `backend/mcp/internal_tools_server.py` 暴露 internal tools |
| OAuth MCP | 未实现 |
| Token storage | 未实现 |
| 前端 | Profile 页可触发 observation；无 external source connect UI |

## 5. 方案调研与选择

### 5.1 调研问题

| 问题 | 结论 |
| --- | --- |
| 是否直接接真实 SaaS？ | 首版只做 **1 个最小只读源**；若真实 provider 不稳定，允许用本地 OAuth stub / demo MCP server 验证协议 |
| OAuth 流程 | 采用 OAuth 2.1 authorization code + PKCE；token 只在后端保存 |
| MCP 形态 | HTTP remote MCP / connector adapter 作为候选；不替换 V4-D stdio internal MCP |
| 导入路径 | OAuth 拉取候选 items → 创建 `external_import_batch` pending → 用户 confirm 后才可被 observation 引用 |
| 失败语义 | connect / fetch 失败 fail-fast 给用户；已确认历史 context 不受影响 |
| scope | 只读最小 scope；不请求 write / admin |
| external evidence | 只能作为 supplementary context，不成为 report primary evidenceRefs 或 profile positive evidence |

### 5.2 方案对比

| 方案 | 优点 | 缺点 | 决定 |
| --- | --- | --- | --- |
| A 继续 mock import | 简单 | 不能验证 production OAuth | 拒绝作为 V5-C 主路径 |
| B 真实 OAuth provider + connector | 最接近目标 | provider 差异大，token 安全复杂 | 首选，限制 1 个只读源 |
| C 本地 OAuth stub + MCP demo server | 可控、可测 | 不是真实 SaaS | 可作为 fallback / CI path |
| D background sync | 用户体验好 | 违反 V5-0 用户确认边界 | 拒绝 |
| E external write tools | 能力更强 | 治理风险过大 | 拒绝 |

### 5.3 首选路径

```text
ExternalSourceConnector protocol
→ OAuthConnectionService（connect / callback / disconnect）
→ ExternalSourceImportService（fetch preview items）
→ existing ExternalImportRepository.create_batch(...)
→ existing confirm / reject
→ observation tool registry only reads confirmed items
```

V5-C 首版应尽量复用 V4-D `CreateExternalImportRequest` 与 `ExternalImportBatch`，避免重写 confirm 语义。

## 6. 系统边界

### 6.1 必做

- [ ] 配置：`EXTERNAL_SOURCE_RUNTIME=mock_oauth|mcp_oauth|disabled`。
- [ ] Schema + migration：external OAuth connection / token metadata（token secret 不返回前端）。
- [ ] `ExternalSourceConnector` protocol：只读 `list_items()`，输出 `ExternalContextItemDraft`。
- [ ] OAuth connect / callback / disconnect service。
- [ ] 最小 PKCE：`code_verifier` 后端保存；`code_challenge=S256`。
- [ ] Token storage：后端持久化 access / refresh token（首版可明文 dev-only；必须在 debug / docs 标注风险，生产加密 deferred 到 V5-D 或 V6）。
- [ ] API：connect URL、callback、connection status、fetch preview / create import batch。
- [ ] 前端：Profile 或 External Context 页显示连接状态、拉取候选、确认 / 拒绝批次。
- [ ] Debug / audit：connection status、sourceSystem、scopes、last fetch、import batch id。
- [ ] Tests：OAuth state/user scope、pending batch、confirm 后可读、reject 后不可读、cross-user forbidden。

### 6.2 不做

- [ ] 不做后台自动同步。
- [ ] 不做 external write tools。
- [ ] 不做多个 SaaS connector marketplace。
- [ ] 不做企业 IAM / SSO。
- [ ] 不把 external context 写入 profile positive evidence。
- [ ] 不让 external context 作为 report insight 的 primary evidenceRefs。
- [ ] 不在前端保存 token。
- [ ] 不把 token / auth code / refresh token 写入 debug payload。

## 7. 契约设计

### 7.1 Runtime 配置

候选：

```env
EXTERNAL_SOURCE_RUNTIME=disabled|mock_oauth|mcp_oauth
EXTERNAL_SOURCE_PROVIDER=demo_notes|notion|readwise
EXTERNAL_SOURCE_CLIENT_ID=
EXTERNAL_SOURCE_CLIENT_SECRET=
EXTERNAL_SOURCE_REDIRECT_URI=http://127.0.0.1:8000/api/users/{user_id}/external-sources/oauth/callback
EXTERNAL_SOURCE_REQUIRED_SCOPES=read
```

默认：

```text
disabled
```

原因：

- CI / dev 默认不依赖外部 SaaS。
- 用户显式启用后才暴露连接入口。

### 7.2 后端数据模型（候选）

新增表：

```text
external_source_connections
```

字段候选：

| 字段 | 说明 |
| --- | --- |
| id | connection id |
| user_id | V5-A scope |
| provider | demo_notes / notion / readwise / mcp_server |
| status | disconnected / pending_authorization / connected / expired / revoked / failed |
| scopes_json | 已授权只读 scope |
| access_token_ciphertext | token 存储；首版 dev-only 明文需显性记录 |
| refresh_token_ciphertext | 可空 |
| token_expires_at | 可空 |
| resource_uri | MCP resource indicator / server canonical URI |
| created_at | 创建时间 |
| updated_at | 更新时间 |
| last_connected_at | 最近连接时间 |
| last_error | 最近错误（不含 secret） |

可选表：

```text
external_oauth_states
```

字段候选：

| 字段 | 说明 |
| --- | --- |
| state | OAuth state，随机不可预测 |
| user_id | 发起用户 |
| provider | provider |
| code_verifier | PKCE verifier（短 TTL） |
| redirect_after | 回跳页面 |
| created_at | 创建时间 |
| expires_at | 过期时间 |

### 7.3 API 设计（候选）

```text
GET  /api/users/{user_id}/external-sources
POST /api/users/{user_id}/external-sources/{provider}/connect
GET  /api/users/{user_id}/external-sources/{provider}/oauth/callback
POST /api/users/{user_id}/external-sources/{provider}/disconnect
POST /api/users/{user_id}/external-sources/{provider}/imports/preview
```

说明：

- `connect` 返回 authorization URL，不返回 token。
- `callback` 校验 state + PKCE，创建 / 更新 connection。
- `preview` 调 connector 拉取候选 items，并复用 existing import batch pending confirmation。
- `confirm` / `reject` 继续复用：

```text
POST /api/users/{user_id}/external-imports/{batch_id}/confirm
POST /api/users/{user_id}/external-imports/{batch_id}/reject
```

### 7.4 Connector 契约

```text
ExternalSourceConnector
├── provider_name
├── required_scopes
├── build_authorization_url(...)
├── exchange_code(...)
├── refresh_token(...)
└── list_items(connection, limit) -> list[ExternalContextItemDraft]
```

约束：

- `list_items` 只能返回标题、摘要、sourceUri、tags。
- connector 不直接写数据库。
- connector 不做 LLM 总结。
- connector 不决定是否导入；导入由用户 confirm 决定。

## 8. Prompt / Workflow / Agent 边界

V5-C 不新增 report prompt。

Agent observation 边界：

- 仅 confirmed external context 可进入 tool registry。
- 输出必须继续带 disclaimer。
- external context 的 refs 应标记为 `external_ctx_*`，不能伪装成 `input_*`。
- external context 不参与 profile positive evidence 写入。

可选 workflow：

```text
connect external source
→ OAuth callback
→ preview external items
→ create pending import batch
→ user confirm / reject
→ observation reads confirmed items
```

## 9. 验收标准

### 9.1 自动验证

- [x] `EXTERNAL_SOURCE_RUNTIME=disabled`：现有 V4-D / V5-A / V5-B 测试通过。
- [x] mock OAuth runtime：connect → callback → status connected。
- [x] preview 创建 pending `external_import_batch`，不自动 confirmed。
- [x] confirm 后 import batch 变为 confirmed。
- [ ] reject 后 confirmed items 不可见（待人工/补充自动验证）。
- [x] cross-user 不可读取 / confirm / reject 他人的 connection 或 batch。
- [x] token / auth code / refresh token 不出现在 API response / debug response。
- [ ] Agent observation 不把 external context 写入 profile positive evidence（沿用 V4-D 测试，待 V5-C 手工确认）。

自动验证记录：

```text
backend: python -m pytest -q → 113 passed, 5 warnings
frontend: npm run build → passed
```

### 9.2 人工验证

- [x] 前端可看到 external source 连接状态。
- [x] 用户点击 connect 后完成授权回跳。
- [x] 用户点击 preview 后看到候选外部上下文。
- [x] 未 confirm 前 observation 不引用该批次。
- [x] confirm 后 external import batch 状态变为 confirmed，并显示 supplementary disclaimer。
- [x] database backend 恢复后，`/external-sources` smoke test 返回 200。
- [ ] disconnect 后无法继续拉取新 items；已确认历史批次保留或按 §11 决策处理（未测，非阻塞）。

### 9.3 安全 / 治理验收

- OAuth `state` 绑定 user + provider，不能跨用户复用。
- PKCE verifier 只在后端短期保存。
- scope 为只读最小集合。
- 所有 connection / import APIs 走 `require_user_scope`。
- 不记录 secret 到 logs / debug / frontend。
- external context 不作为 primary evidence / profile positive evidence。

## 10. AI 生成代码顺序（候选）

1. Config + schemas：runtime、connection、OAuth state、response models。
2. Migration + repository：connection/state store。
3. Connector protocol + mock OAuth connector。
4. OAuth service：connect URL、callback exchange、disconnect、status。
5. Import preview service：connector list_items → existing `CreateExternalImportRequest`。
6. API routes：external-sources。
7. Frontend service + minimal UI。
8. Agent / tool registry boundary check（confirmed-only）。
9. Tests：unit + integration + governance。
10. Docs：`docs/12`、`docs/15`、`docs/README`、必要时 `docs/11` / `docs/13`。

## 11. 用户确认（已接受，2026-06-22）

- [x] 接受 V5-C 首版范围：**1 个只读外部源 + OAuth/PKCE + preview/import/confirm**。
- [x] 接受 `EXTERNAL_SOURCE_RUNTIME=disabled|mock_oauth|mcp_oauth`，默认 disabled。
- [x] 接受首版可以用 **mock OAuth / demo MCP server** 做自动化路径；真实 SaaS 若不稳定不阻塞主线。
- [x] 接受 token 首版后端保存；生产级加密 / secret manager 作为 V5-D/V6 明确风险项，不在 V5-C 扩大。
- [x] 接受 **不做 background sync**，每次导入必须用户触发 preview 并 confirm。
- [x] 接受 external context 只作为 supplementary context，不写 profile positive evidence，不作为 report primary evidence。
- [x] 接受 V5-C 完成后进入 V5-D Resilience & Observability。

## 12. 权威设计文档更新判断

V5-C 确认后、实现前建议：

- `docs/11`：新增 ExternalSourceConnector / OAuth connection / import preview API 契约。
- `docs/13`：新增 OAuth state、token redaction、external context governance 测试项。
- `docs/19`：补充 external context 不进入 profile positive evidence 的长期记忆规则（如尚未充分覆盖）。

本任务单草案阶段暂不修改权威正文。

## 13. 当前结论

```text
V5-C 已验收通过，状态 accepted / manual_validation_passed。
已实现：EXTERNAL_SOURCE_RUNTIME、external source connection/state schema、migration、
mock_oauth connector、external-sources API、Profile 页 connect/preview/confirm UI。
验证：pytest 113 passed；frontend build passed；database smoke test 200。
验收修复：本地 PostgreSQL/Python 连接恢复；Alembic head 已确认。
下一子阶段：V5-D Resilience, Observability & Tech-debt（任务单待起草）。
```
