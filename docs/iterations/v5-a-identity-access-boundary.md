# V5-A：Identity & Access Boundary

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V4 archived baseline 之上，建立 **持久用户身份与 API 对象级访问边界**：

```text
持久 anonymous session（或 dev bypass）
↓
CurrentUser 解析与 request scope
↓
/api/users/{user_id}/... 对象级隔离
↓
服务层不再硬编码 user_anonymous
↓
现有 user_anonymous 数据兼容与迁移
```

本轮完成后，系统应能：

- 新访客通过 session bootstrap 获得持久 `user_id`，刷新页面后仍识别同一用户。
- 用户 A 无法通过 API 读取用户 B 的 report / profile / timeline / agent 数据（`AUTH_MODE=anonymous_session`）。
- 本地开发与 pytest 仍可通过 `AUTH_MODE=dev` 使用固定 `user_anonymous`（与 V4 测试兼容）。
- debug 面板可见当前 `authMode` 与 `resolvedUserId`。

## 2. 上游版本决策

引用 `docs/iterations/v5-0-production-runtime-trust-boundary-research.md` §12 已确认：

- V5-A 先于 Real LLM report（V5-B）与 OAuth MCP（V5-C）。
- 不做企业 SSO、复杂 RBAC、多租户计费。
- identity 变更不得破坏 V1–V4 evidence-first / memory governance。
- V5-B 依赖稳定 user scope 与 audit 边界。

## 3. 本轮解决什么问题

```text
如何把 dev 模式下硬编码的 user_anonymous，升级为可持久、可隔离、可测试的用户身份与 API scope，且 dev/CI 仍可 bypass？
```

本轮不解决：

- 登录 / magic link / 邮箱验证（可 V5-C 前或 V6+ 扩展，本轮不做）。
- Real LLM report runtime（V5-B）。
- OAuth MCP（V5-C）。
- Chroma graceful degrade（V5-D）。
- 前端完整账户设置页。

## 4. 当前实现快照（V5-A 起点）

| 能力 | 当前状态 |
| --- | --- |
| `users` 表 | 已存在 `UserModel(id, anonymous_id, created_at, updated_at)` |
| 用户创建 | `DatabaseProfileRepository._ensure_user` 按需 insert |
| API 路径 | `/api/users/{user_id}/...` 广泛存在，**无** ownership 校验 |
| 服务层 | `analysis_job_service`、`input_service`、`feedback_service` 等硬编码 `"user_anonymous"` |
| 前端 | `App.tsx` 常量 `CURRENT_USER_ID = "user_anonymous"` |
| 认证 | 无 middleware、无 session、无 cookie |
| 测试 | `conftest` memory backend；大量测试使用 `user_anonymous` |

## 5. 外部调研与方案选择

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| 主身份路径 | **持久 anonymous session**（HttpOnly cookie + server-side session 记录） |
| dev / test | `AUTH_MODE=dev`：允许任意 path `user_id`，默认 `user_anonymous` |
| production-like | `AUTH_MODE=anonymous_session`：path `user_id` 必须等于 resolved user |
| Session 存储 | PostgreSQL `user_sessions` 表（database 模式）；memory backend 用 in-memory dict |
| Bootstrap API | `POST /api/session/bootstrap` → `{ userId, sessionToken, authMode }` + Set-Cookie |
| 现有数据 | migration 确保 `user_anonymous` 用户行存在；历史数据归属不变 |
| 跨域 | 前端 dev proxy + `allow_credentials=True`（已配置 CORS credentials） |

### 5.2 不采用方案

| 方案 | 原因 |
| --- | --- |
| 纯 localStorage user_id 无服务端校验 | 用户可伪造他人 ID，无 trust boundary |
| JWT 自包含 anonymous id | V5-A 不需要分布式 auth；session 表更简单、可撤销 |
| 强制 magic link 登录 | 超出 V5-A scope；阻塞 V5-B |
| 每个 resource 改 URL 去掉 user_id | 改动面过大；保留 REST 路径，加 scope 校验 |

### 5.3 最终方案选择

#### 5.3.1 配置项

```text
AUTH_MODE=dev|anonymous_session     # 默认 dev（本地/CI 兼容）
SESSION_COOKIE_NAME=aesthetic_session
SESSION_TTL_DAYS=365                # 持久 anonymous，长 TTL
```

#### 5.3.2 数据模型

**扩展 `users`（可选，若 session 表已足够则不改 users）：**

- 保持 `id` 为 canonical user_id（UUID 字符串）。
- `anonymous_id` 保留兼容；新用户 `anonymous_id` 可等于 `id` 或 null。

**新增 `user_sessions`：**

```text
id              PK (session token, uuid)
user_id         FK → users.id
created_at
expires_at
last_seen_at
```

#### 5.3.3 API 契约

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/session/bootstrap` | 无 cookie 时创建 user + session；有有效 cookie 时返回现有 user |
| GET | `/api/session/me` | 返回 `{ userId, authMode }` |
| * | `/api/users/{user_id}/*` | `anonymous_session` 下 `user_id` ≠ current → **403** |

非 user-scoped 路由（health、部分 admin）保持公开；`POST /api/inputs`、`POST /api/analysis-jobs` 等 **改为**从 current user 取 id，不再 body 内任意 userId（若 body 有 userId 则必须与 current 一致或忽略）。

#### 5.3.4 后端模块

```text
app/core/auth.py              # get_current_user, require_user_scope
app/api/deps.py               # FastAPI Depends
app/api/routes/session.py     # bootstrap / me
app/repositories/session_repository.py
app/services/session_service.py
```

#### 5.3.5 服务层改造范围

替换硬编码 `"user_anonymous"` 为 `current_user_id: str` 参数或 context：

- `AnalysisJobService.create_job`
- `InputService.create_input`
- `FeedbackService` 全部方法
- `FileStorage` 默认 user（upload 绑定 current user）
- Agent / observation 入口（已接 path user_id，加 scope 即可）

Repository 查询 **已有** `user_id` 过滤的保持不变；需补全 report-by-id、job-by-id 等 **ownership check**。

#### 5.3.6 前端

```text
src/app/session.ts            # bootstrapSession(), getCurrentUserId()
src/app/App.tsx               # 启动时 bootstrap，Context 提供 userId
src/api/client.ts             # credentials: 'include'；URL 使用 dynamic userId
```

UI：Debug 或设置区显示当前 userId（dev 可见即可）。

#### 5.3.7 测试策略

- `conftest`：`AUTH_MODE=dev`，行为与现基线一致 → **96 passed 不退化**。
- 新增 `test_v5a_identity.py`：
  - anonymous_session：A 不能读 B 的 report/profile。
  - bootstrap 幂等：同 cookie 返回同 user。
  - dev mode：仍可用 user_anonymous。
- 新增 `test_v5a_governance_validation.py`（轻量）：scope 违规不泄露 existence（统一 403 或 404，需在实现时定一种并文档化）。

## 6. 系统边界

### 6.1 必做

- [ ] `AUTH_MODE` 配置与文档化。
- [ ] Session bootstrap + cookie + `/api/session/me`。
- [ ] `get_current_user` dependency + user-scoped route 校验。
- [ ] 服务层去除硬编码 `user_anonymous`（dev 模式默认仍可为 user_anonymous）。
- [ ] Alembic migration：`user_sessions` + `user_anonymous` backfill。
- [ ] 前端 session bootstrap + dynamic userId。
- [ ] 单元 / 集成测试 + governance 测试。
- [ ] debug trace：`authMode`、`resolvedUserId`（可选 `sessionId` 前缀）。

### 6.2 不做

- [ ] 邮箱 / OAuth 登录。
- [ ] RBAC / admin 角色。
- [ ] 跨设备 account merge。
- [ ] Real LLM / MCP / resilience。

## 7. 架构影响

### 7.1 后端

- `app/core/config.py`：`auth_mode`、cookie 名、TTL。
- 新 session 模块；`main.py` 注册 session router。
- 所有 `/api/users/{user_id}/` routes 加 `require_user_scope`。
- `database_repositories`：session CRUD。

### 7.2 前端

- Session provider；API client credentials。
- 移除硬编码 `CURRENT_USER_ID`（dev fallback 可读 env）。

### 7.3 权威文档（实现前/后）

- `docs/07`：users / user_sessions 表与 auth 数据流。
- `docs/11`：session API、auth dependency 契约。
- `docs/13`：V5-A scope 治理检查项。
- `docs/19`：若 persistent identity 影响 memory 语义（预计 § 用户标识 小幅补充）。

## 8. 验收标准

### 8.1 自动化

- memory backend pytest ≥ 96 passed（含 V4 回归）。
- V5-A 新增测试全部通过。
- Alembic upgrade head 无 pending。

### 8.2 人工验证

- `AUTH_MODE=anonymous_session`：两浏览器 profile 隔离；A 改 URL 访问 B → 403。
- 刷新页面后同一浏览器 userId 不变。
- `AUTH_MODE=dev`：现有手动流程与 V4 一致。
- Debug 可见 auth 边界。

### 8.3 人工验收清单

- [x] bootstrap 创建新用户并 Set-Cookie。
- [x] 同 cookie 再次 bootstrap 返回同一 userId。
- [x] scoped API 跨 user 访问被拒绝。
- [x] 分析 → 报告 → 反馈链路在 anonymous_session 下端到端可用。
- [x] V4-E governance 测试仍通过。
- [x] Debug 可见 authContext（authMode / resolvedUserId / sessionPresent）。
- [x] dev 模式历史/画像与 user_anonymous 对齐（bootstrap 修复后）。

## 9. AI 生成代码顺序（候选）

1. Config + auth models/schemas
2. Migration + session repository
3. Session service + routes (bootstrap/me)
4. `get_current_user` + scope dependency
5. 改造 user-scoped routes + services（去硬编码）
6. Frontend session bootstrap
7. Tests (unit + integration + governance)
8. Debug trace + docs/15

## 10. 权威设计文档更新判断

```text
V5-A 方案确认后、实现开始前：
- docs/07：user_sessions、auth 数据流
- docs/11：session API、scope 规则
- docs/13：V5-A governance 检查项
实现完成后更新 docs/15 §27。
```

## 11. 用户确认（已接受，2026-06-17）

- [x] 接受主路径为 **持久 anonymous session（HttpOnly cookie + user_sessions 表）**。
- [x] 接受 `AUTH_MODE=dev` 作为本地/CI bypass，默认行为与 V4 `user_anonymous` 兼容。
- [x] 接受 `AUTH_MODE=anonymous_session` 下跨 user 访问返回 **403**。
- [x] 接受 **不做** 邮箱登录 / SSO / RBAC。
- [x] 确认后按 §9 顺序开始实现。

## 12. 当前结论

```text
V5-A 已验收通过，状态 accepted / manual_validation_passed。
已实现：session bootstrap/me、AUTH_MODE dev|anonymous_session、API scope、服务层去硬编码、
Alembic user_sessions、前端 session bootstrap + Debug authContext。
验收修复：dev bootstrap 固定 user_anonymous；profile_item ID 按 user 隔离。
pytest：100+ passed（含 test_v5a_identity.py）。
下一子阶段：V5-B Real Report Runtime（版本级任务单待起草，§11 确认后实现）。
```
