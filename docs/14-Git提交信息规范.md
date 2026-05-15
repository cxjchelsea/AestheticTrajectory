# Git 提交信息规范

## 1. 目标

Git 提交信息用于说明一次代码变更的意图、范围和影响。

好的提交信息应该让协作者在不打开完整 diff 的情况下，也能快速判断：

- 这次改了什么类型的问题。
- 为什么要做这次修改。
- 是否影响功能、接口、数据结构或构建流程。
- 后续排查问题时应该从哪个提交开始看。

## 2. 推荐格式

推荐使用接近 Conventional Commits 的写法：

```text
<type>(<scope>): <subject>
```

示例：

```text
feat(auth): add login token refresh
fix(report): handle empty analysis result
docs: update project setup guide
```

其中：

- `type` 表示变更类型。
- `scope` 表示影响范围，可选。
- `subject` 用一句话说明这次提交做了什么。

如果提交内容比较复杂，可以使用正文：

```text
feat(report): add aesthetic summary generation

Generate a structured summary from user preference records.
This prepares the report module for later visualization.
```

## 3. 常见 type 写法

### feat

新增功能。

```text
feat(profile): add user aesthetic preference model
feat(upload): support image upload
```

适合用于：

- 新增页面、接口、模块。
- 新增用户可感知的能力。
- 新增系统内部的重要能力。

### fix

修复问题。

```text
fix(api): return empty list when no records exist
fix(report): avoid crash on missing tags
```

适合用于：

- 修复 bug。
- 修复边界情况。
- 修复错误返回、异常崩溃或展示问题。

### docs

只修改文档。

```text
docs: add git commit message guide
docs(readme): update local startup steps
```

适合用于：

- README。
- 接口说明。
- 设计文档。
- 注释文档。

### style

只调整代码风格，不改变逻辑。

```text
style(ui): format component layout
style: apply prettier formatting
```

适合用于：

- 格式化。
- 空格、缩进、换行。
- 命名或排版上的轻微调整。

注意：如果修改影响了逻辑，不应使用 `style`。

### refactor

重构代码，但不改变外部行为。

```text
refactor(analysis): split prompt builder from service
refactor(db): simplify query helper
```

适合用于：

- 拆分函数。
- 调整模块结构。
- 提取公共方法。
- 改善代码可维护性。

### test

新增或修改测试。

```text
test(report): add cases for empty analysis result
test(api): cover upload validation
```

适合用于：

- 单元测试。
- 集成测试。
- 测试数据。
- 测试工具。

### chore

日常维护类修改。

```text
chore: update dependencies
chore(config): adjust eslint rules
```

适合用于：

- 依赖升级。
- 配置调整。
- 构建脚本维护。
- 不直接影响业务功能的工程事务。

### build

影响构建系统或依赖管理。

```text
build: add vite config
build(deps): upgrade typescript
```

适合用于：

- 打包配置。
- 构建工具。
- package 管理。
- CI 构建相关配置。

### ci

影响持续集成流程。

```text
ci: add lint check workflow
ci(github): run tests on pull request
```

适合用于：

- GitHub Actions。
- CI/CD 脚本。
- 自动化检查流程。

### perf

性能优化。

```text
perf(search): cache embedding lookup result
perf(api): reduce repeated database queries
```

适合用于：

- 减少重复计算。
- 减少请求次数。
- 优化查询。
- 改善响应速度。

### revert

回滚提交。

```text
revert: revert "feat(report): add chart export"
```

适合用于：

- 回退某个错误提交。
- 临时撤销有风险的变更。

## 4. scope 的写法

`scope` 用于说明本次提交影响的范围。它应该简短、稳定、容易理解。

常见写法：

```text
feat(auth): add login page
fix(api): validate request payload
docs(readme): add environment setup
refactor(report): extract summary generator
```

可以按以下维度选择：

- 按功能模块：`auth`、`report`、`upload`、`profile`。
- 按技术层：`api`、`db`、`ui`、`config`。
- 按文档范围：`readme`、`docs`、`guide`。

如果范围不明确，可以省略：

```text
docs: add commit message guide
chore: update project scripts
```

## 5. subject 写法

`subject` 是提交标题中最重要的部分，建议遵守以下规则：

- 使用简短的动词开头，例如 `add`、`fix`、`update`、`remove`、`split`、`rename`。
- 描述本次提交的结果，而不是描述自己做了什么。
- 不要写成流水账。
- 不要过长，尽量控制在一行内。
- 英文项目中通常使用小写开头，不以句号结尾。

推荐：

```text
fix(report): handle empty preference records
refactor(api): extract response formatter
docs: add deployment notes
```

不推荐：

```text
fix bug
update code
修改了一些东西
完成今天的任务
wip
```

## 6. 常见提交示例

新增功能：

```text
feat(upload): support multiple image selection
```

修复空数据问题：

```text
fix(report): show fallback message for empty analysis
```

调整接口返回结构：

```text
refactor(api): normalize analysis response shape
```

新增测试：

```text
test(analysis): cover invalid preference input
```

更新文档：

```text
docs: add git commit message guide
```

升级依赖：

```text
chore(deps): update frontend dependencies
```

添加 CI 检查：

```text
ci: run lint and tests on pull requests
```

## 7. 多行提交信息模板

当一次提交需要说明背景、影响或迁移方式时，可以使用多行提交信息：

```text
feat(report): add aesthetic trajectory summary

Generate a summary from historical analysis records so the report page
can show the user's preference changes over time.

This does not change the existing analysis API response.
```

正文建议说明：

- 为什么需要这次修改。
- 主要变更是什么。
- 是否有兼容性影响。
- 是否需要额外迁移或配置。

## 8. Breaking Change 写法

如果提交包含破坏性变更，需要明确标注。

方式一：在 type 后加 `!`。

```text
feat(api)!: rename analysis result fields
```

方式二：在正文中写 `BREAKING CHANGE`。

```text
feat(api): rename analysis result fields

BREAKING CHANGE: `tags` is replaced by `aestheticTags`.
Clients must update their response parsing logic.
```

适合用于：

- 删除或重命名公开接口字段。
- 改变数据库结构且需要迁移。
- 删除已有配置项。
- 改变对外可见行为。

## 9. 中文提交信息写法

如果团队更习惯中文，也可以保留同样结构：

```text
feat(报告): 新增审美轨迹摘要生成
fix(上传): 修复空文件提交时报错
docs: 补充本地启动说明
refactor(分析): 拆分 prompt 构建逻辑
```

中文写法也应避免过于笼统：

不推荐：

```text
修改代码
修复问题
更新文件
```

推荐：

```text
fix(报告): 处理分析结果为空时的展示
docs: 新增 Git 提交信息规范
```

## 10. 日常使用建议

- 一次提交只做一类事情，避免把功能、格式化、重构和文档混在一起。
- 提交前先查看 diff，确认提交内容和提交信息一致。
- 如果只是临时保存，可以使用 `wip`，但合并前应整理成清晰提交。
- 提交信息优先说明意图，不只是描述文件变化。
- 公共分支上的提交应比个人实验分支更规范。

## 11. 快速选择表

| 场景 | 推荐 type | 示例 |
| --- | --- | --- |
| 新增功能 | `feat` | `feat(report): add summary generation` |
| 修复 bug | `fix` | `fix(api): validate empty payload` |
| 修改文档 | `docs` | `docs: add setup guide` |
| 代码格式化 | `style` | `style: format source files` |
| 代码重构 | `refactor` | `refactor(db): extract query helper` |
| 新增测试 | `test` | `test(upload): cover file validation` |
| 依赖或配置维护 | `chore` | `chore(deps): update dependencies` |
| 构建相关 | `build` | `build: update vite config` |
| CI 相关 | `ci` | `ci: add test workflow` |
| 性能优化 | `perf` | `perf(api): reduce duplicate queries` |
| 回滚提交 | `revert` | `revert: revert "feat(report): add export"` |

## 12. 推荐模板

简单提交：

```text
<type>(<scope>): <subject>
```

复杂提交：

```text
<type>(<scope>): <subject>

<why this change is needed>
<what changed at a high level>
<anything reviewers or future maintainers should know>
```

破坏性变更：

```text
<type>(<scope>)!: <subject>

BREAKING CHANGE: <migration or compatibility note>
```
