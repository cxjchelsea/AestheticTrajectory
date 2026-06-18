# Aesthetic Trajectory

AI aesthetic analysis product for exploring long-term personal preference modeling.

The current project has an accepted and archived V2 Memory / User Model baseline.

## Scope

- V0 frontend prototype: home, upload, analysis waiting, and report pages.
- V1 stable baseline: FastAPI routes, Pydantic schemas, memory/database repositories, mock AI workflow, report API, feedback API, PostgreSQL persistence, and `analysis_logs`.
- V2-A report history: historical report list API, frontend history page, empty state, and report detail review.
- V2-B profile evidence: `user_profiles`, `profile_items`, `profile_evidence`, read-only profile API, and profile evidence UI.
- V2-C feedback governance: feedback updates the current profile snapshot without duplicating evidence.
- V2-D report comparison: latest two-report comparison API and frontend comparison page.
- V2-E memory governance validation: evidence coverage, rejected interpretation handling, uncertain feedback handling, and non-diagnostic expression checks.
- V3-A personalized history retrieval: workflow history retrieval step, `ReportResponse.historyContext`, and report detail history reference UI.
- V3-B aesthetic knowledge RAG: static knowledge base retrieval, `ReportResponse.knowledgeContext`, and report detail knowledge reference UI.
- V3-C evaluation metrics baseline: workflow evaluation step, evaluation API, report detail metrics UI.
- V3-D retrieval / RAG observability: debug API retrieval/context/evaluation trace, Developer Debug Panel sections.
- Current validation status: backend tests pass (48 passed with memory, 6 passed with database), frontend production build passes, V3-A through V3-D manual validation passed.
- Not included yet: real model calls, real image feature extraction, ChromaDB runtime writes, external knowledge RAG runtime, Agent, MCP, knowledge graph, or long-term profile automation beyond the V2 lightweight baseline.

V1 validation is archived in `docs/archive/v1/`. V2 is archived in `docs/archive/v2/`. V3-0 is accepted in `docs/iterations/v3-0-personalized-retrieval-research.md`. V3-A through V3-D are accepted; next step is V3-E per `docs/12-开发任务拆分与里程碑计划.md`.

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
- `GET /api/users/{user_id}/reports/comparison/latest`
- `GET /api/users/{user_id}/profile`
- `GET /api/insights/{insight_id}/feedback`
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
- `docs/iterations/v3-0-personalized-retrieval-research.md`
- `docs/15-迭代执行记录.md`
- `docs/16-V1开发收口清单.md`
- `docs/archive/v1/`
- `docs/archive/v2/`
