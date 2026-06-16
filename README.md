# Aesthetic Trajectory

AI aesthetic analysis product for exploring long-term personal preference modeling.

The current project is a V0/V1 skeleton: it validates the frontend flow, FastAPI API shape, mock AI workflow, structured report response, and insight feedback loop.

## Scope

- V0 frontend prototype: home, upload, analysis waiting, and report pages with local mock data.
- V1 backend skeleton: FastAPI routes, Pydantic schemas, in-memory repositories, mock AI workflow, report API, and feedback API.
- Current validation status: backend tests pass, frontend production build passes, and API flow integration is covered.
- Not included yet: real model calls, real image feature extraction, PostgreSQL runtime persistence, ChromaDB runtime writes, RAG, Agent, MCP, knowledge graph, or long-term profile.

V1 skeleton / baseline validation is archived in `docs/archive/v1/`. V1-A and V1-B are accepted and archived; the next development task is `docs/iterations/v1-c-report-feedback.md`.

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
- `docs/iterations/v1-c-report-feedback.md`
- `docs/15-迭代执行记录.md`
- `docs/16-V1开发收口清单.md`
- `docs/archive/v1/`
