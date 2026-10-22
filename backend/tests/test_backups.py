"""Tests for backup service and routes."""

from __future__ import annotations

import os

from backend.app.services.backup_service import (
    create_backup,
    list_backups,
    prune_old_backups,
    restore_sqlite,
)


def test_create_and_list_backup(tmp_path, monkeypatch):
    db_file = tmp_path / "app.db"
    import sqlite3

    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'hello')")
    conn.commit()
    conn.close()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    from backend.app.config import reset_settings_cache

    reset_settings_cache()

    path = create_backup()
    assert path is not None
    assert path.exists()
    assert len(list_backups()) == 1

    # restore
    target = tmp_path / "restored.db"
    restore_sqlite(str(path), str(target))
    assert target.exists()
    conn = sqlite3.connect(str(target))
    row = conn.execute("SELECT v FROM t WHERE id=1").fetchone()
    conn.close()
    assert row == ("hello",)


def test_prune(monkeypatch, tmp_path):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    from backend.app.config import reset_settings_cache

    reset_settings_cache()
    (tmp_path / "backups").mkdir()
    old = tmp_path / "backups" / "backup_old.sqlite3"
    old.write_text("x")
    import time

    os.utime(old, (time.time() - 40 * 86400, time.time() - 40 * 86400))
    removed = prune_old_backups(retention_days=30)
    assert removed == 1
