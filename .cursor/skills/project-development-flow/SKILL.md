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

First split the project into a version roadmap. Then run every version through this loop:

```text
问题定义 -> 边界 -> 契约 -> 数据 -> 接口 -> Prompt/Skill/Workflow -> AI 生成 -> 测试 -> 重构 -> 复盘
```

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

For each independently acceptable iteration, establish these before implementation:

1. Iteration goal: version, target, hypothesis, and what the user can do afterward.
2. Problem definition: what this iteration solves, what it does not solve, and why it comes now.
3. Research and option choice: existing products, papers, frameworks, reusable patterns, and final approach.
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

## Project Documentation Targets

Use the current repository documentation structure:

- Iteration task sheets: `docs/iterations/`
- Development plan and AI generation order: `docs/12-开发任务拆分与里程碑计划.md`
- Test and validation evidence: `docs/13-验证与评估文档.md`
- Iteration execution record and retrospective: `docs/15-迭代执行记录.md`
- Version closure checklist: `docs/16-V1开发收口清单.md`
- Archived completed-version facts: `docs/archive/`

When updating docs, keep project-level docs for durable decisions and iteration docs for per-round evidence.

Every implementation iteration must create or update one file under `docs/iterations/` as the factual record for that round.

## Implementation Discipline

- Prefer the repository's existing architecture, naming, and helper APIs.
- Keep each iteration focused on one core loop or acceptance target.
- Do not let AI invent database fields, API paths, permission rules, or core state transitions without checking the relevant design docs.
- For Agent or LLM work, require structured inputs, output schema, failure handling, and validation tests.
- After implementation, run the appropriate tests and update the iteration record with commands, results, remaining risks, and next step.

## Full Template

For the complete fill-in template, examples, and project-level sections, read `workflow-template.md`.
