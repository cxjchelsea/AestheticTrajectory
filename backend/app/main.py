from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    analysis_jobs,
    aesthetic_knowledge,
    external_sources,
    feedback,
    files,
    health,
    inputs,
    observations,
    profiles,
    reports,
    session,
    timeline,
)
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(session.router, prefix="/api")
    app.include_router(files.router, prefix="/api")
    app.include_router(inputs.router, prefix="/api")
    app.include_router(analysis_jobs.router, prefix="/api")
    app.include_router(reports.router, prefix="/api")
    app.include_router(profiles.router, prefix="/api")
    app.include_router(timeline.router, prefix="/api")
    app.include_router(aesthetic_knowledge.router, prefix="/api")
    app.include_router(observations.router, prefix="/api")
    app.include_router(external_sources.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    return app


app = create_app()
