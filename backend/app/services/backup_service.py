"""Backup and recovery utilities for the application database."""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("app.services.backup")


def _backup_dir() -> Path:
    d = Path(get_settings().backup_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def backup_sqlite(db_path: str, destination: Path | None = None) -> Path:
    """Create a consistent backup of a sqlite database."""
    src = Path(db_path)
    if not src.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")
    dest_dir = destination or _backup_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"backup_{_timestamp()}.sqlite3"
    # Use sqlite backup API for consistency
    src_conn = sqlite3.connect(str(src))
    dst_conn = sqlite3.connect(str(dest))
    try:
        src_conn.backup(dst_conn)
    finally:
        src_conn.close()
        dst_conn.close()
    logger.info("SQLite backup created", extra={"path": str(dest)})
    return dest


def backup_postgres(database_url: str, destination: Path | None = None) -> Path | None:
    """Run pg_dump if available; return backup path or None."""
    dest_dir = destination or _backup_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"backup_{_timestamp()}.sql"
    try:
        with open(dest, "w", encoding="utf-8") as out:
            subprocess.run(
                ["pg_dump", database_url],
                stdout=out,
                check=True,
            )
    except FileNotFoundError:
        logger.warning("pg_dump not available; skipping postgres backup")
        if dest.exists():
            dest.unlink()
        return None
    except subprocess.CalledProcessError as exc:
        logger.error("pg_dump failed", extra={"error": str(exc)})
        if dest.exists():
            dest.unlink()
        return None
    logger.info("Postgres backup created", extra={"path": str(dest)})
    return dest


def create_backup() -> Path | None:
    settings = get_settings()
    url = settings.database_url
    if url.startswith("sqlite"):
        # extract path
        path = url.replace("sqlite:///", "").replace("sqlite://", "")
        path = path.removeprefix("./")
        return backup_sqlite(path)
    return backup_postgres(url)


def restore_sqlite(backup_path: str, target_path: str) -> None:
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")
    dst = Path(target_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    logger.info("SQLite restored", extra={"backup": str(src), "target": str(dst)})


def list_backups() -> list[Path]:
    d = _backup_dir()
    if not d.exists():
        return []
    return sorted(d.glob("backup_*"), reverse=True)


def prune_old_backups(retention_days: int = 30) -> int:
    cutoff = datetime.now(UTC).timestamp() - retention_days * 86400
    removed = 0
    for p in list_backups():
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
                removed += 1
        except OSError:
            continue
    if removed:
        logger.info("Pruned old backups", extra={"removed": removed})
    return removed
