下面是可直接放进 `V1-E iteration 文档` 的调研记录。我只选了可访问、相对可靠的来源；没有使用无法核验的博客链接。

#### 记录 1：Alembic 官方文档 — Migration 执行、当前版本与 schema drift 检查

来源名称：
Alembic 官方文档：Tutorial / Commands / Autogenerate Check

来源类型：
官方文档 / 数据库 migration 工具文档

链接或出处：
Alembic Tutorial、Commands、Autogenerate Check。Alembic 文档说明 `alembic upgrade head` 会从当前数据库 revision 执行到目标 revision，并使用 `alembic_version` 表记录当前版本；`alembic current` 可显示当前数据库 revision；`alembic check` 可检测模型变更是否还需要生成新的 migration。([Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html))

调研问题：

- 如何确认 migration 已执行？
- 如何确认数据库 revision 已到最新 head？
- 如何发现 SQLAlchemy model 与实际数据库 schema 之间还有未生成的 migration？

核心做法：

- 使用 `alembic upgrade head` 将数据库迁移到最新 revision。
- 使用 `alembic current` 查看当前数据库 revision；当数据库 revision 匹配 head 时，会显示 head 标记。
- 使用 `alembic heads` 查看代码侧 migration 脚本的最新 head。
- 使用 `alembic check` 检测是否还有未生成的 upgrade operations。
- 在自动化或 CI 中可把 `alembic check` 作为防止 schema drift 的检查项。

对 V1-E 的启发：

- V1-E 的 migration 验收不能只看服务是否启动，必须明确记录：`alembic upgrade head` 已执行成功。
- 对 PostgreSQL 持久化基线，应记录 `alembic current` 输出，确认当前数据库 revision 已到 head。
- 对 SQLAlchemy + Alembic 项目，应增加 `alembic check`，确认当前 model 与数据库结构之间没有遗漏 migration。
- 对 `analysis_logs` 表，不能只依赖 ORM 可访问；应确认 migration 后表真实存在、字段存在、可写入、可查询。
- 对 V1-E 归档，应把 migration 命令、输出摘要、执行时间、数据库环境写入验收记录。

不能照搬：

- Alembic 文档主要说明 migration 工具机制，不提供完整产品验收规范。
- `alembic check` 只能发现 autogenerate 能识别的 schema 差异；不能替代业务级数据读写验证。
- V1-E 当前是稳定基线验收，不需要引入复杂多分支 migration 管理。

采用结论：

```text
本项目采用 alembic upgrade head + alembic current + alembic heads + alembic check 作为 migration 自动验收基线；不把服务能启动等同于 migration 验收通过。
```

------

#### 记录 2：PostgreSQL 官方文档 — information_schema 表结构检查

来源名称：
PostgreSQL 官方文档：Information Schema / tables view

来源类型：
官方文档 / 数据库 schema 检查资料

链接或出处：
PostgreSQL 官方文档说明 `information_schema` 是一组描述当前数据库对象的视图，且标准化、相对稳定；`information_schema.tables` 包含当前用户有权限访问的表和视图。([PostgreSQL](https://www.postgresql.org/docs/current/information-schema.html))

调研问题：

- 如何确认 migration 后 PostgreSQL 表真实存在？
- 如何确认 schema 正确，而不是仅依赖 ORM 代码？
- 如何给 V1-E 留下可审计的数据库验收记录？

核心做法：

- 使用 `information_schema.tables` 检查目标表是否存在。
- 使用 `information_schema.columns` 检查关键字段是否存在、类型是否符合预期。
- 使用实际 SQL 查询检查表是否可读。
- 使用一次业务路径写入检查表是否可写。
- 使用 PostgreSQL 直接查询结果作为验收记录，而不是只看接口返回。

对 V1-E 的启发：

- 对 `analysis_logs` 必须检查：表存在、主键存在、分析记录字段存在、时间字段存在、状态或 metadata 字段存在。
- 对 embedding metadata、similarity grouping、report、insight、feedback 相关持久化表，应至少检查核心表和核心字段。
- 对 FastAPI 接口，应通过 pytest 或手动流程触发一次完整分析，再到 PostgreSQL 查询是否落库。
- 对 V1-D 到 V1-E 的验收，应证明数据不是只存在内存里，而是 PostgreSQL 可查询、可复现。
- 对 iteration 文档，应附上数据库检查 SQL 和实际返回摘要。

不能照搬：

- `information_schema` 适合检查标准表、列、约束信息，但不一定覆盖所有 PostgreSQL 专有能力。
- 当前 V1-E 不需要做完整 DBA 级审计，例如索引性能分析、权限矩阵、备份恢复演练。
- 不需要为每个非核心字段都写复杂校验，重点放在演示链路所依赖的核心表和字段。

采用结论：

```text
本项目采用 PostgreSQL information_schema + 实际 SELECT 查询作为 schema 与数据可查询验收依据；不只依赖 SQLAlchemy model 或接口成功返回。
```

------

#### 记录 3：Google SRE — Launch Checklist / Release Readiness

来源名称：
Google SRE Book：Deployment Strategies for Product Launches / Launch Coordination Checklist

来源类型：
发布工程资料 / SRE 实践资料

链接或出处：
Google SRE 说明 launch checklist 的目的，是降低失败、保证一致性和完整性；同时也强调 checklist 不能无限膨胀，需要在成本和收益之间保持平衡。示例检查项包括是否存储持久化数据、是否需要备份、是否可能被滥用、是否需要限流等。([Google SRE](https://sre.google/sre-book/reliable-product-launches/))

调研问题：

- V1-E 发布/归档前 checklist 应包括哪些项？
- 如何避免 checklist 过度复杂，反而不适合 V1-E？
- 对一个可演示系统，release readiness 应该检查什么？

核心做法：

- 使用 checklist 确保发布前检查一致、完整。
- checklist 应围绕真实风险，而不是无限罗列。
- 对存储持久化数据的系统，应检查数据保存、查询、备份或恢复策略。
- 对可被用户使用的服务，应考虑滥用、异常输入、限流或保护机制。
- checklist 应给出 action item，而不是只问抽象问题。

对 V1-E 的启发：

- V1-E 不是真正大规模生产发布，但应该有“稳定基线归档 checklist”。
- checklist 应覆盖：测试是否通过、migration 是否执行、PostgreSQL 数据是否可查、核心 API 是否可用、前端演示路径是否走通、反馈是否可保存。
- 对 `analysis_logs`，应明确它是 V1-E 的验收证据表：能记录分析请求、结果状态、关键 metadata、时间。
- 对 FastAPI，应检查服务启动、核心接口、错误返回、日志记录。
- 对 React 前端，应检查最小演示路径，而不是追求完整 UI 测试自动化。

不能照搬：

- Google SRE 的 checklist 面向生产级服务，包含大规模运维、SLO、容量、滥用防护、跨团队协作。
- 当前 V1-E 是个人项目稳定基线验收，不需要完整 SRE PRR，也不需要复杂监控体系。
- 不需要引入正式发布审批流程，但需要有归档记录和阻塞项判断。

采用结论：

```text
本项目采用轻量 release readiness checklist：测试、migration、数据库、核心链路、前端手动验收、日志与遗留问题归档；不采用生产级 SRE 全量发布流程。
```

------

#### 记录 4：ISTQB Glossary — Smoke Test 定义

来源名称：
ISTQB Glossary：Smoke Test

来源类型：
测试方法说明 / 行业术语标准

链接或出处：
ISTQB 将 smoke test 定义为覆盖组件或系统主要功能的一组测试，用于判断系统在计划测试开始前是否基本工作正常。([ISTQB 术语表](https://glossary.istqb.org/en_US/term/smoke-test?exact_matches_first=true&term=sanity&utm_source=chatgpt.com))

调研问题：

- 冒烟测试的定义是什么？
- V1-E 应如何设计 smoke test？
- smoke test 与完整回归测试边界是什么？

核心做法：

- 冒烟测试覆盖主功能，不追求深度覆盖。
- 冒烟测试用于判断当前构建是否值得继续测试。
- 冒烟测试应短、稳定、可重复。
- 冒烟测试失败通常意味着当前版本不能进入后续验收。
- 冒烟测试应优先覆盖核心路径，而不是边缘场景。

对 V1-E 的启发：

- V1-E smoke test 应覆盖“系统是否能演示”：后端启动、数据库连接、核心 API 返回、前端页面打开、一次分析流程完成。
- 对 FastAPI，应至少跑通健康检查接口或核心分析接口。
- 对 PostgreSQL，应确认连接成功、migration 已到 head。
- 对 `analysis_logs`，应确认一次核心分析会产生日志记录。
- 对 React 前端，应手动确认上传/输入、触发分析、查看 report/insight、提交 feedback 的主路径可用。

不能照搬：

- 不应把 smoke test 扩展成所有 pytest、所有 UI 路径、所有异常输入测试。
- 不应把 V1-E smoke test 做成复杂端到端自动化框架；当前阶段更适合“少量 pytest + 手动主路径”。
- smoke test 不能证明系统没有缺陷，只能证明主链路可继续验收。

采用结论：

```text
本项目采用 smoke test 作为 V1-E 第一层验收：只验证最小可演示主链路是否可运行；不把 smoke test 当作完整质量证明。
```

------

#### 记录 5：ISTQB Glossary — Regression Testing 定义

来源名称：
ISTQB Glossary：Regression Testing

来源类型：
测试方法说明 / 行业术语标准

链接或出处：
ISTQB 将 regression testing 定义为一种变更相关测试，用于检测软件未变更区域是否因为改动而引入或暴露缺陷。([ISTQB 术语表](https://glossary.istqb.org/en_US/term/regression-testing?utm_source=chatgpt.com))

调研问题：

- 回归测试的定义是什么？
- V1-E 应如何设计 regression test？
- V1-E 回归测试应覆盖哪些历史能力？

核心做法：

- 回归测试关注“变更是否破坏已有能力”。
- 回归测试不只测新增功能，也要测未改动但受影响的旧功能。
- 回归测试应围绕历史稳定能力和高风险路径。
- 回归测试适合自动化，尤其是 API、数据处理、持久化逻辑。
- 回归测试范围应根据当前 iteration 的改动风险选择。

对 V1-E 的启发：

- V1-E 是最终稳定基线，应回归 V1-A 到 V1-D 的核心能力。
- V1-A 回归：特征抽取边界仍稳定，不因 persistence 改动而变化。
- V1-B 回归：embedding metadata 与 similarity grouping 仍能生成和读取。
- V1-C 回归：report、insight、feedback 仍能正常生成和保存。
- V1-D 回归：PostgreSQL persistence 与 `analysis_logs` 仍能写入、查询、关联到一次分析。
- pytest 应优先覆盖后端 API、service 层、数据库读写，不强行覆盖 React UI 细节。

不能照搬：

- 不需要为 V1-A 到 V1-D 每个历史细节都做完整回归。
- 不需要引入大型测试管理平台。
- 不应把所有视觉样式、交互细节都纳入自动回归；前端当前更适合手动验收记录。

采用结论：

```text
本项目采用面向 V1-A 至 V1-D 核心能力的轻量 regression test：优先自动化 API、service、database；前端以手动验收补充。
```

------

#### 记录 6：Microsoft Learn — Manual Test 执行与结果记录

来源名称：
Microsoft Learn：Run Manual Tests with Azure Test Plans

来源类型：
官方文档 / 手动测试记录规范

链接或出处：
Microsoft Learn 说明手动测试执行时，应逐步标记 pass/fail；失败时可记录 comment、诊断数据，并创建或关联 bug；测试结束后保存结果并查看测试状态。文档还指出，如果有验证步骤失败或未标记，整体测试用例会失败。([Microsoft Learn](https://learn.microsoft.com/en-us/azure/devops/test/run-manual-tests?view=azure-devops))

调研问题：

- 手动验收记录应该包含什么？
- 前端手动验收如何做到可追踪？
- 失败结果和 bug / 遗留问题如何关联？

核心做法：

- 每个测试步骤应有预期结果。
- 每个验证步骤应标记 passed / failed。
- 失败时记录失败原因、评论、截图或诊断信息。
- 失败项应创建或关联 bug。
- 测试结束后保存测试状态，便于回看历史结果。

对 V1-E 的启发：

- React 前端手动验收记录应包含：页面路径、操作步骤、输入样例、预期结果、实际结果、是否通过。
- 对 report / insight / feedback 页面，应记录“能否展示、能否提交、提交后是否写入 PostgreSQL”。
- 对 `analysis_logs`，手动验收不能只写“前端成功”，还要记录对应日志 ID 或查询结果。
- 对限制项应单独写：当前未做鉴权、未做大规模并发、未做 UI 自动化、未做生产监控。
- 对失败项应明确归类为 blocking 或 non-blocking，并写入 iteration 归档。

不能照搬：

- Azure Test Plans 是完整测试管理平台，当前项目不需要引入。
- 不需要建立复杂测试套件管理界面。
- 当前只需要 Markdown 文档中的手动验收表格即可。

采用结论：

```text
本项目采用 Markdown 手动验收记录：路径、步骤、预期结果、实际结果、状态、证据、遗留问题；不引入 Azure Test Plans 等测试管理平台。
```

------

#### 记录 7：ISTQB + Atlassian — Severity / Priority / Blocked 分类

来源名称：
ISTQB Glossary：Severity；Atlassian Jira：Priority / Severity / Blocked

来源类型：
测试术语标准 / 缺陷管理实践资料

链接或出处：
ISTQB 将 severity 定义为缺陷对组件或系统开发、运行的影响程度。Atlassian 将 priority 定义为问题相对其他问题的重要性，severity 是影响程度，blocked 是团队成员无法继续推进的情况；Jira 默认优先级包括 blocker、critical、major、minor、trivial。([ISTQB 术语表](https://glossary.istqb.org/en_US/term/severity?utm_source=chatgpt.com))

调研问题：

- 阻塞问题和非阻塞遗留问题如何分类？
- blocking、severity、priority 有什么区别？
- V1-E 归档时哪些问题必须修，哪些可以留到 V2？

核心做法：

- severity 描述影响程度：系统崩溃、数据丢失、核心功能不可用属于高严重度。
- priority 描述修复顺序：即使问题严重，也要结合当前版本目标判断是否必须立刻修。
- blocked 表示当前工作无法继续推进。
- blocker / critical / major / minor / trivial 可作为问题分级词汇。
- 问题分类应结合用户影响、数据风险、核心路径、是否有绕过方案、是否影响验收。

对 V1-E 的启发：

- V1-E 的 blocking issue 应定义为：影响可演示、可持久化、可反馈稳定基线成立的问题。
- 如果 FastAPI 核心分析接口失败、PostgreSQL migration 未执行、`analysis_logs` 无法写入、反馈无法保存，应判定为阻塞。
- 如果 UI 文案不完美、样式不统一、非核心边缘输入未处理，可作为非阻塞遗留。
- 如果问题影响 V1-A 到 V1-D 的已完成能力，应提高优先级。
- 所有遗留问题必须写明：影响范围、是否有 workaround、计划处理版本。

不能照搬：

- Jira 的 blocker / critical / major 等默认优先级不能直接等同于本项目的验收结论。
- V1-E 不需要复杂 issue tracking workflow。
- 不应因为一个问题名称叫 critical 就自动阻止归档，必须结合 V1-E 目标判断。

采用结论：

```text
本项目采用“是否破坏 V1-E 稳定基线”作为 blocking 判断标准；采用 severity 描述影响，priority 决定修复顺序，不机械照搬 Jira 默认等级。
```

------

## V1-E 建议采用方案

### 一、自动验收 checklist

```text
[ ] pytest 全量通过
[ ] FastAPI TestClient 核心 API flow 通过
[ ] V1-A 特征抽取边界测试通过
[ ] V1-B embedding metadata / similarity grouping 测试通过
[ ] V1-C report / insight / feedback 测试通过
[ ] V1-D PostgreSQL persistence 测试通过
[ ] alembic upgrade head 执行成功
[ ] alembic current 显示数据库 revision 已到 head
[ ] alembic heads 与 current 对齐
[ ] alembic check 无 pending upgrade operations
[ ] 核心 API 调用后 PostgreSQL 可查询到对应数据
[ ] 核心 API 调用后 analysis_logs 产生记录
```

### 二、手动验收 checklist

```text
[ ] React 前端可正常启动
[ ] 首页 / 主分析页可访问
[ ] 用户可输入或上传审美分析对象
[ ] 用户可触发分析
[ ] 前端可展示 report
[ ] 前端可展示 insight
[ ] 用户可提交 feedback
[ ] feedback 提交后页面有明确反馈
[ ] 手动查询 PostgreSQL 可看到对应 feedback 或分析结果
[ ] 手动查询 analysis_logs 可看到本次分析记录
[ ] 记录本次验收路径、输入样例、预期结果、实际结果
[ ] 记录未覆盖范围：并发、鉴权、生产部署、复杂异常输入、UI 自动化
[ ] 记录遗留问题及 blocking / non-blocking 分类
```

### 三、PostgreSQL 表检查 checklist

```text
[ ] 数据库连接成功
[ ] alembic_version 表存在
[ ] alembic_version 当前 revision 与代码 head 一致
[ ] analysis_logs 表存在
[ ] V1-B embedding metadata 相关表存在
[ ] V1-B similarity grouping 相关表存在
[ ] V1-C report / insight / feedback 相关表存在
[ ] 核心表主键存在
[ ] 核心表 created_at / updated_at 或等价时间字段存在
[ ] 核心表可 SELECT
[ ] 核心表可 INSERT 或由业务 API 写入
[ ] 核心表写入后可按 ID 或 analysis_id 查询
```

建议保留的 SQL 验收片段：

```sql
SELECT version_num FROM alembic_version;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'analysis_logs'
ORDER BY ordinal_position;

SELECT *
FROM analysis_logs
ORDER BY created_at DESC
LIMIT 5;
```

### 四、analysis_logs 检查 checklist

```text
[ ] 每次核心分析请求会生成 analysis_logs 记录
[ ] analysis_logs 记录包含唯一 ID
[ ] analysis_logs 记录包含请求或分析类型
[ ] analysis_logs 记录包含状态，例如 success / failed
[ ] analysis_logs 记录包含时间字段
[ ] analysis_logs 记录能关联到 report / insight / feedback 或至少能定位一次分析
[ ] 分析成功时记录 success
[ ] 分析失败时记录 failed 或错误摘要
[ ] 手动验收记录中写入对应 analysis_logs ID 或最近一条查询结果
```

### 五、阻塞项 / 非阻塞遗留项分类规则

#### 阻塞项 blocking

满足任一条件即阻塞 V1-E 归档：

```text
[ ] FastAPI 服务无法启动
[ ] PostgreSQL 无法连接
[ ] alembic upgrade head 失败
[ ] alembic current 未到 head
[ ] alembic check 发现未生成 migration，且影响核心表
[ ] 核心分析 API 无法完成
[ ] report / insight 无法生成
[ ] feedback 无法保存
[ ] analysis_logs 不生成记录
[ ] 核心数据只存在内存，PostgreSQL 不可查询
[ ] 前端主演示路径无法走通
[ ] pytest 核心用例失败
[ ] 出现数据丢失、错误覆盖、不可恢复异常
```

#### 非阻塞遗留项 non-blocking

满足以下条件可进入 V2 或后续 iteration：

```text
[ ] UI 样式不统一，但不影响主流程
[ ] 文案、提示语、布局存在优化空间
[ ] 非核心异常输入未完全覆盖
[ ] 暂未实现 UI 自动化测试
[ ] 暂未实现鉴权
[ ] 暂未实现生产级日志监控
[ ] 暂未实现并发压测
[ ] 暂未实现备份恢复演练
[ ] 个别 insight 解释质量可优化，但 report 生成链路稳定
[ ] 有明确 workaround，不影响 V1-E 可演示、可持久化、可反馈基线
```

### 六、V1-E 最终采用结论

```text
V1-E 稳定版验收采用“自动测试 + migration 检查 + PostgreSQL 直接查询 + 前端手动验收 + analysis_logs 证据归档”的轻量 release readiness 方案。

通过标准不是“功能看起来能用”，而是：
1. V1-A 至 V1-D 核心能力未回退；
2. migration 已执行且 schema 与 SQLAlchemy model 无明显漂移；
3. PostgreSQL 中可查询到核心分析、反馈与日志数据；
4. 前端主路径可演示；
5. analysis_logs 能作为验收证据；
6. 不存在破坏可演示、可持久化、可反馈稳定基线的 blocking issue。

不采用生产级 SRE 发布流程、不引入大型测试管理平台、不强制前端 UI 自动化；这些内容归入 V2 或生产化阶段。
```