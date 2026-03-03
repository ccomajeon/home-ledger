from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()


def _normalize_sqlite_url(url: str) -> str:
    if not url.startswith("sqlite:///"):
        return url

    raw_path = url.replace("sqlite:///", "", 1)
    if raw_path in {"", ":memory:"}:
        return url

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        db_path = backend_root / db_path

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


db_url = _normalize_sqlite_url(settings.db_url)

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
