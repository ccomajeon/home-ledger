import os
from collections.abc import Iterator

import pytest

os.environ["DB_URL"] = "sqlite:///:memory:"
os.environ["OWNER_EMAIL"] = "owner@example.com"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["BACKUP_DIR"] = "./data/test-backups"

from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.base import Base
from app.db.seed import seed_defaults
from app.db.session import SessionLocal, engine
from app.main import app
from app.utils.security import create_session_token


@pytest.fixture(autouse=True)
def reset_database() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_defaults(db)
    yield


@pytest.fixture
def test_client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def owner_client(test_client: TestClient) -> TestClient:
    test_client.cookies.set(
        get_settings().session_cookie_name,
        create_session_token("owner@example.com"),
    )
    return test_client
