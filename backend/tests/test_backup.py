import sqlite3
from pathlib import Path

import pytest

from app.db import backup


def _value(path: Path) -> str:
    with sqlite3.connect(path) as connection:
        return connection.execute("SELECT value FROM sample").fetchone()[0]


def test_backup_and_restore_round_trip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_path = tmp_path / "app.db"
    backup_path = tmp_path / "backups"
    backup_path.mkdir()
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE sample (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sample VALUES ('before')")

    monkeypatch.setattr(backup, "database_path", lambda: database_path)
    monkeypatch.setattr(backup, "backup_directory", lambda: backup_path)

    created = backup.create_backup()
    with sqlite3.connect(database_path) as connection:
        connection.execute("UPDATE sample SET value = 'after'")
    assert _value(database_path) == "after"

    backup.restore_backup(created.name)

    assert _value(database_path) == "before"
    assert (backup_path / created.name).is_file()


def test_restore_rejects_path_traversal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(backup, "backup_directory", lambda: tmp_path)

    with pytest.raises(ValueError, match="Invalid backup name"):
        backup.restore_backup("../app.db")
