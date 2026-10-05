"""Real PostgreSQL fixtures; each test owns an isolated, disposable schema."""
import os
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, text

from backend.app.core.config import Settings
from backend.app.db.session import create_engine_and_factory
from backend.app.db.seed import seed_database

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def credentials():
    return {
        "SEED_ADMIN_EMAIL": "admin@pravaha.local", "SEED_ADMIN_PASSWORD": "AdminPass123!",
        "SEED_PM_EMAIL": "pm001@pravaha.local", "SEED_PM_PASSWORD": "ManagerPass123!",
        "SEED_TL_EMAIL": "tl001@pravaha.local", "SEED_TL_PASSWORD": "LeaderPass123!",
    }


@pytest.fixture
def db_schema():
    return f"pravaha_test_{uuid4().hex}"


@pytest.fixture
def settings(db_schema):
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("TEST_DATABASE_URL is required: backend database/API tests use genuine PostgreSQL, never SQLite or a production schema.")
    return Settings(_env_file=None, app_env="test", database_url=database_url, db_schema=db_schema, cors_origins=["http://localhost:5174"])


@pytest.fixture
def engine(settings):
    admin_engine = create_engine(settings.database_url, pool_pre_ping=True)
    # The schema name is generated here, validated by Settings, and never supplied by a user.
    with admin_engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{settings.db_schema}"'))
    test_engine, _ = create_engine_and_factory(settings)
    try:
        config = Config(str(ROOT / "backend" / "alembic.ini"))
        with test_engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        yield test_engine
    finally:
        test_engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{settings.db_schema}" CASCADE'))
        admin_engine.dispose()


@pytest.fixture
def session_factory(engine):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def session(session_factory):
    with session_factory() as db_session:
        yield db_session
        db_session.rollback()


@pytest.fixture
def seeded_session_factory(session_factory, credentials):
    with session_factory() as db_session, db_session.begin():
        seed_database(db_session, credentials)
    return session_factory


@pytest.fixture
def app(settings, seeded_session_factory, engine, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    from backend.app.main import create_app
    return create_app(settings, session_factory=seeded_session_factory, engine=engine)


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def identities(client):
    cookies = {}
    for kind, email, password in (
        ("admin", "admin@pravaha.local", "AdminPass123!"),
        ("pm", "pm001@pravaha.local", "ManagerPass123!"),
        ("tl", "tl001@pravaha.local", "LeaderPass123!"),
    ):
        result = client.post("/api/auth/login", json={"email": email, "password": password})
        assert result.status_code == 200, result.text
        cookies[kind] = result.headers["set-cookie"].split(";", 1)[0]
    client.cookies.clear()
    return cookies
