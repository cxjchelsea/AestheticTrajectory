# Aesthetic Trajectory

V0/V1 skeleton for an AI aesthetic analysis product.

## Scope

- V0 frontend prototype: home, upload, analysis waiting, and report pages with local mock data.
- V1 backend skeleton: FastAPI routes, Pydantic schemas, in-memory repositories, and a mock AI workflow.
- Not included yet: real model calls, RAG, Agent, MCP, knowledge graph, long-term profile, PostgreSQL runtime connection, or ChromaDB runtime connection.

## Frontend

```bash
cd frontend
npm install
npm run dev
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
