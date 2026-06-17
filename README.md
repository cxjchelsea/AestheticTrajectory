# Aesthetic Trajectory

AI aesthetic analysis product for exploring long-term personal preference modeling.

The current project has an accepted V2-B lightweight profile implementation and a V2-C feedback weighting implementation that has passed automated validation.

## Scope

- V0 frontend prototype: home, upload, analysis waiting, and report pages.
- V1 stable baseline: FastAPI routes, Pydantic schemas, memory/database repositories, mock AI workflow, report API, feedback API, PostgreSQL persistence, and `analysis_logs`.
- V2-A report history: historical report list API, frontend history page, empty state, and report detail review.
- V2-B profile evidence: `user_profiles`, `profile_items`, `profile_evidence`, read-only profile API, and profile evidence UI.
- Current validation status: backend tests pass, frontend production build passes, SQLite migration validation has passed, PostgreSQL runtime validation has passed, profile API integration is covered, V2-B frontend manual acceptance has passed, and V2-C automated validation has passed.
- Not included yet: real model calls, real image feature extraction, report comparison, ChromaDB runtime writes, RAG, Agent, MCP, knowledge graph, or long-term profile automation.

V1 validation is archived in `docs/archive/v1/`. V2-A is accepted and archived in `docs/iterations/v2-a-report-history.md`; V2-0 Memory / User Model research is accepted in `docs/iterations/v2-0-memory-user-model-research.md`; V2-B is accepted in `docs/iterations/v2-b-profile-evidence.md`. The current development step is V2-C frontend manual validation in `docs/iterations/v2-c-feedback-weight-memory-update.md`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
cd frontend
npm run build
```

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend exposes:

- `GET /api/health`
- `POST /api/inputs`
- `POST /api/analysis-jobs`
- `GET /api/analysis-jobs/{job_id}`
- `GET /api/reports/{report_id}`
- `GET /api/users/{user_id}/reports`
- `GET /api/users/{user_id}/profile`
- `POST /api/insights/{insight_id}/feedback`

Test check:

```bash
cd backend
python -m pytest
```

Reset local/test PostgreSQL business data:

```bash
python scripts/reset_database.py
```

This keeps schema and Alembic migration records, clears only project business tables, and asks for a `RESET <database>` confirmation before running.

## Documentation

Start with:

1. `docs/00-文档体系说明.md`
2. `docs/01-产品概念说明书.md`
3. `docs/02-版本迭代路线图.md`
4. `docs/03-MVP功能需求文档.md`

Current execution and validation:

- `docs/12-开发任务拆分与里程碑计划.md`
- `docs/iterations/v2-a-report-history.md`
- `docs/15-迭代执行记录.md`
- `docs/16-V1开发收口清单.md`
- `docs/archive/v1/`
