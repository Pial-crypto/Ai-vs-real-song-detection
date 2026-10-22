"""Database engine, session management, and helpers."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("app.database")

Base = declarative_base()

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _make_engine() -> Engine:
    settings = get_settings()
    url = settings.database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(
        url,
        pool_size=settings.db_pool_size if not url.startswith("sqlite") else 1,
        max_overflow=settings.db_max_overflow if not url.startswith("sqlite") else 0,
        echo=settings.db_echo,
        connect_args=connect_args,
        future=True,
    )

    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    logger.info("Database engine created", extra={"url": _redact_url(url)})
    return engine


def _redact_url(url: str) -> str:
    if "@" in url and "://" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            creds, host = rest.rsplit("@", 1)
            return f"{scheme}://***:***@{host}"
    return url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _make_engine()
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine(), future=True
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a DB session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for DB sessions outside request scope."""
    db = get_session_factory()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (dev convenience; production uses Alembic)."""
    from backend.app import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables ensured")


def check_db_health() -> bool:
    """Return True if DB is reachable."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Database health check failed", extra={"error": str(exc)})
        return False


def reset_engine() -> None:
    """Reset cached engine/session (used in tests)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
