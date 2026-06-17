---
name: project-development-flow
description: Follow this project's AI-assisted development workflow. Use when starting project planning, a new version, feature iteration, milestone, acceptance pass, refactor, documentation pass, or when the user asks to develop according to the fixed project process.
---

# Project Development Flow

## When To Use

Use this skill before implementing or planning:

- New project planning, version planning, or MVP scoping.
- A new feature, iteration, milestone, refactor, or acceptance pass.
- Documentation updates that record design, validation, iteration status, or project closure.
- Any request mentioning the fixed development process, project workflow, iteration flow, V1/V2 work, or "按项目开发流程".

## Core Rule

First split the project into a version roadmap. Before implementing any major version, run a version-level research and architecture gate. Only then split the version into implementation iterations.

Version-level gate:

```text
产品概念 / Agent 前沿方向
-> 版本级调研
-> 版本能力地图
-> 版本架构边界
-> 子阶段拆分
-> 子阶段执行
```

For each implementation iteration, use this loop:

```text
问题定义 -> 边界 -> 契约 -> 数据 -> 接口 -> Prompt/Skill/Workflow -> AI 生成 -> 测试 -> 重构 -> 复盘
```

Do not jump directly from one accepted version into a feature slice of the next version. Establish the version hypothesis, Agent frontier directions, memory/user-model implications, capability map, sub-stage dependencies, and acceptance criteria first.

Do not jump directly into code for iteration work. Establish the target, boundary, contracts, data/API impact, and acceptance criteria first.

For every implementation iteration, complete research and option selection before editing code. Do not implement until the chosen approach, boundaries, and acceptance criteria are recorded.

## Project-Level Planning

Project-level planning is done once at the start of a project, then maintained as the project changes.

Check or update the relevant docs:

- Project positioning and total goal: `docs/01-产品概念说明书.md`
- Version roadmap: `docs/02-版本迭代路线图.md`
- MVP scope and "not doing" boundaries: `docs/03-MVP功能需求文档.md`
- System architecture and data design: `docs/07-数据结构与系统架构文档.md`
- Module boundaries and interface tests: `docs/11-模块拆分与接口测试文档.md`
- Validation strategy and technical risks: `docs/13-验证与评估文档.md`

For a new project, fill the project-level sections in `workflow-template.md`.

## Iteration Workflow

Before creating the first implementation iteration of a major version, create a version-level task sheet under `docs/iterations/`, such as `v2-0-memory-user-model-research.md`.

The version-level task sheet must record:

1. Which Agent frontier directions from `docs/01-产品概念说明书.md` this version advances.
2. The version-level research questions.
3. The capability map for the whole version.
4. Memory / user model write, update, forget, conflict, explainability, and governance rules if the version touches memory.
5. The sub-stage split and dependency order.
6. Which decisions are version-level and cannot be reinvented by sub-stages.
7. The version-level acceptance criteria.

After a version-level gate is accepted, promote durable decisions into the authoritative design docs before starting implementation sub-stages. Do not leave architecture, memory rules, data model decisions, module contracts, validation metrics, or governance rules only in `docs/iterations/`.

Do not mechanically update authoritative design docs in every iteration. At the start and end of each iteration, explicitly decide whether the iteration affects durable design. Only update `docs/04` to `docs/11` or other authoritative docs when the work changes long-lived architecture, data models, API contracts, workflow, prompt contracts, module boundaries, validation metrics, governance rules, or implementation-vs-design alignment. If it does not, record "No authoritative design doc update required" in the iteration sheet.

Design promotion targets:

- Product / Agent direction changes: `docs/01-产品概念说明书.md` or `docs/02-版本迭代路线图.md`
- Data structures, memory model, storage boundaries, and system architecture: `docs/07-数据结构与系统架构文档.md`
- Module responsibilities, inputs, outputs, dependencies, and interface tests: `docs/11-模块拆分与接口测试文档.md`
- Validation metrics, evaluation methods, and governance checks: `docs/13-验证与评估文档.md`
- Execution plan and current next step: `docs/12-开发任务拆分与里程碑计划.md`
- Actual execution record and retrospective: `docs/15-迭代执行记录.md`

For each independently acceptable iteration, establish these before implementation:

1. Iteration goal: version, target, hypothesis, and what the user can do afterward.
2. Problem definition: what this iteration solves, what it does not solve, and why it comes now.
3. Research and option choice: existing products, papers, frameworks, reusable patterns, and final approach. Separate version-level research from implementation-level research.
4. System boundary: included capabilities, postponed capabilities, explicit non-goals, and reasons.
5. Acceptance criteria: function, effect, exception, security/permission, and documentation checks.
6. Architecture impact: frontend, backend, database, runtime, tools, memory layer, and call flow.
7. Module contracts: responsibility, upstream/downstream dependencies, inputs, outputs, errors, permissions, and acceptance.
8. Data model: entities, fields, relationships, states, indexes, queries, and lifecycle.
9. API design: name, path, method, request, response, errors, and permissions.
10. Prompt / Skill / Workflow design: LLM usage, prompt input/output schema, failure handling, skill trigger, tools, and output standard.
11. AI code generation plan: generation order, required inputs, human review checkpoints, and decisions AI must not invent.
12. Review and testing: unit, API, end-to-end, exception, LLM stability, and security tests.
13. Refactor pass: naming, shared abstractions, duplicate logic, types, and missing tests.
14. Documentation and retrospective: design notes, module/API/prompt docs, run notes, test records, unfinished work, failure cases, next target, reusable modules, and reusable skills.

If an item does not apply, explicitly record "不涉及" in the iteration documentation instead of omitting it.

Every sub-stage must cite its upstream version-level decisions. If no version-level gate exists for the major version, stop and create it before implementation.

## Version Closure And Archive Gate

Before marking any major version as accepted or moving to the next major version, run a version closure gate.

Version closure must include:

1. A version closure checklist, such as `docs/16-V1开发收口清单.md` or `docs/17-V2开发收口清单.md`.
2. An archive folder under `docs/archive/vX/`.
3. A version acceptance checklist in the archive folder.
4. A version legacy issue list in the archive folder.
5. A version archive summary in the archive folder.
6. Updates to `docs/15-迭代执行记录.md`, `docs/12-开发任务拆分与里程碑计划.md`, and `docs/README.md`.

Legacy issues must be reviewed before starting the next major version. Each item must be classified as:

- `resolved`: completed by the current or later version.
- `carry_over`: still relevant and explicitly assigned to a later version.
- `blocking`: must be fixed before the current version can be archived.
- `wont_fix`: intentionally closed with a reason.

Do not leave legacy issues as a plain list without owner version, impact, and status. If a previous version has unresolved `blocking` items, stop and resolve or reclassify them before starting new version work.

## Project Documentation Targets

Use the current repository documentation structure:

- Iteration task sheets: `docs/iterations/`
- Development plan and AI generation order: `docs/12-开发任务拆分与里程碑计划.md`
- Test and validation evidence: `docs/13-验证与评估文档.md`
- Iteration execution record and retrospective: `docs/15-迭代执行记录.md`
- Version closure checklist: `docs/<NN>-V<version>开发收口清单.md`
- Archived completed-version facts: `docs/archive/`

When updating docs, keep project-level docs for durable decisions and iteration docs for per-round evidence.

Every implementation iteration must create or update one file under `docs/iterations/` as the factual record for that round.

## Implementation Discipline

- Prefer the repository's existing architecture, naming, and helper APIs.
- Keep each iteration focused on one core loop or acceptance target.
- Do not let AI invent database fields, API paths, permission rules, or core state transitions without checking the relevant design docs.
- For Agent or LLM work, require structured inputs, output schema, failure handling, and validation tests.
- After implementation, run the appropriate tests and update the iteration record with commands, results, remaining risks, and next step.

## AI Governance And Debuggability

- Development defaults to fail fast. Do not add fallback, default objects, empty arrays, compatibility branches, or skipped validation just to make a task continue.
- A fallback is allowed only when an authoritative design doc explicitly permits degradation. It must state the trigger, original error, fallback action, user-visible impact, developer message, and test coverage.
- Core business facts must fail rather than degrade: missing inputs, missing reports, invalid feedback targets, schema validation failures, and persistence failures.
- Non-core enhancements may degrade only when the degraded result remains truthful, such as unavailable retrieval, optional history context, or dev-only mock runtime.
- Mock, heuristic, placeholder, and dev-only behavior must be visibly marked and must not be described as real model capability.
- Do not modify tests first when tests fail. Classify whether the failure is implementation, test expectation, requirement drift, or fixture data before changing assertions.
- Do not introduce an interface, factory, registry, configuration switch, or runtime for a future version unless the current iteration acceptance criteria require it.
- Future-version capabilities may be documented or represented as boundary warnings, but must not be implemented as runtime code before their version gate.

## Full Template

For the complete fill-in template, examples, and project-level sections, read `workflow-template.md`.
