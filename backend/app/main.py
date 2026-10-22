"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.database import init_db
from backend.app.errors import register_exception_handlers
from backend.app.logging_config import configure_logging, get_logger
from backend.app.middleware.correlation import CorrelationIdMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.routers import (
    analytics,
    audit,
    auth,
    backups,
    batch,
    dashboards,
    export,
    feature_flags,
    health,
    models,
    notifications,
    prediction,
    predictions,
    profiles,
    search,
    users,
)

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    settings = get_settings()
    logger.info("Starting application", extra={"env": settings.environment, "version": settings.app_version})
    if settings.environment != "production":
        init_db()
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Detect AI-generated music using an ensemble of ML models.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    register_exception_handlers(app)

    api_prefix = settings.api_prefix
    app.include_router(health.router)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(predictions.router, prefix=api_prefix)
    app.include_router(dashboards.router, prefix=api_prefix)
    app.include_router(backups.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(audit.router, prefix=api_prefix)
    app.include_router(batch.router, prefix=api_prefix)
    app.include_router(export.router, prefix=api_prefix)
    app.include_router(feature_flags.router, prefix=api_prefix)
    app.include_router(notifications.router, prefix=api_prefix)
    app.include_router(profiles.router, prefix=api_prefix)
    app.include_router(models.router, prefix=api_prefix)
    app.include_router(search.router, prefix=api_prefix)
    app.include_router(prediction.router)

    return app


app = create_app()
