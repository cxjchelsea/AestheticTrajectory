# Aesthetic Trajectory

AI aesthetic analysis product for exploring long-term personal preference modeling.

The current project has a V2-A report history baseline: it validates the V1 analysis flow plus historical report listing and detail review.

## Scope

- V0 frontend prototype: home, upload, analysis waiting, and report pages.
- V1 stable baseline: FastAPI routes, Pydantic schemas, memory/database repositories, mock AI workflow, report API, feedback API, PostgreSQL persistence, and `analysis_logs`.
- V2-A report history: historical report list API, frontend history page, empty state, and report detail review.
- Current validation status: backend tests pass, frontend production build passes, PostgreSQL runtime validation has passed, and history API integration is covered.
- Not included yet: real model calls, real image feature extraction, lightweight profile, report comparison, ChromaDB runtime writes, RAG, Agent, MCP, knowledge graph, or long-term profile.

V1 validation is archived in `docs/archive/v1/`. V2-A is accepted and archived in `docs/iterations/v2-a-report-history.md`; V2-0 Memory / User Model research is accepted in `docs/iterations/v2-0-memory-user-model-research.md`. The next development step is V2-B lightweight profile data model and profile evidence planning.

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
- `POST /api/insights/{insight_id}/feedback`

Test check:

```bash
cd backend
python -m pytest
```

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
