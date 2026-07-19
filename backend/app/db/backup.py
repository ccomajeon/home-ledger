from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.db.session import engine
from app.schemas import BackupPublic


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def backup_directory() -> Path:
    configured = Path(get_settings().backup_dir)
    path = configured if configured.is_absolute() else _backend_root() / configured
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def database_path() -> Path:
    if engine.url.get_backend_name() != "sqlite" or not engine.url.database:
        raise RuntimeError("Backup is supported only for file-based SQLite databases")
    if engine.url.database == ":memory:":
        raise RuntimeError("In-memory databases cannot be backed up")
    return Path(engine.url.database).resolve()


def create_backup() -> BackupPublic:
    source_path = database_path()
    now = datetime.now(UTC)
    name = f"home-ledger-{now.strftime('%Y%m%d-%H%M%S-%f')}.sqlite3"
    destination_path = backup_directory() / name

    with sqlite3.connect(source_path) as source, sqlite3.connect(
        destination_path
    ) as destination:
        source.backup(destination)

    stat = destination_path.stat()
    return BackupPublic(
        name=name,
        size=stat.st_size,
        created_at=datetime.fromtimestamp(stat.st_mtime, UTC),
    )


def list_backups() -> list[BackupPublic]:
    backups: list[BackupPublic] = []
    for path in backup_directory().glob("*.sqlite3"):
        stat = path.stat()
        backups.append(
            BackupPublic(
                name=path.name,
                size=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_mtime, UTC),
            )
        )
    return sorted(backups, key=lambda item: item.created_at, reverse=True)


def restore_backup(name: str) -> None:
    if Path(name).name != name:
        raise ValueError("Invalid backup name")

    source_path = (backup_directory() / name).resolve()
    if source_path.parent != backup_directory() or not source_path.is_file():
        raise FileNotFoundError(name)

    target_path = database_path()
    engine.dispose()
    with sqlite3.connect(source_path) as source, sqlite3.connect(
        target_path
    ) as destination:
        source.backup(destination)
