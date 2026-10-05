import base64
from datetime import UTC, datetime

from argon2.low_level import Type, hash_secret_raw
from pydantic import ValidationError
import pytest

from backend.app.core.config import Settings
from backend.app.core.security import LoginRateLimiter, digest_token, hash_password, is_valid_password, verify_password

URL = "postgresql+psycopg://fixture:fixture@db.invalid:5432/fixture"


def test_database_configuration_is_mandatory_and_rejects_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    for value in ("sqlite:///workflow.db", "", "mysql://user:pass@db.invalid/name"):
        with pytest.raises(ValidationError):
            Settings(_env_file=None, database_url=value)


def test_neon_style_postgresql_url_and_csv_origins_are_environment_config(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://fixture:fixture@db.invalid/fixture?sslmode=require")
    monkeypatch.setenv("CORS_ORIGINS", "https://frontend.invalid,http://localhost:5199")
    monkeypatch.setenv("API_PORT", "8123")
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.database_url.endswith("?sslmode=require")
    assert settings.cors_origins == ["https://frontend.invalid", "http://localhost:5199"]
    assert settings.api_port == 8123
    assert "fixture:fixture" not in repr(settings)


def test_backend_env_overrides_root_file_and_real_environment_overrides_both(tmp_path, monkeypatch):
    root = tmp_path / "root.env"
    backend = tmp_path / "backend.env"
    root.write_text(f"DATABASE_URL={URL}\nAPI_PORT=8001\n", encoding="utf-8")
    backend.write_text("API_PORT=8002\n", encoding="utf-8")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("API_PORT", raising=False)
    assert Settings(_env_file=(root, backend)).api_port == 8002
    monkeypatch.setenv("API_PORT", "8003")
    assert Settings(_env_file=(root, backend)).api_port == 8003


def test_production_cookie_docs_and_cross_site_constraints():
    production = Settings(_env_file=None, database_url=URL+"?sslmode=require", app_env="production", rate_limit_backend="postgresql", cors_origins=["https://frontend.invalid"])
    assert production.session_cookie_secure is True
    assert production.enable_api_docs is False
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url=URL, app_env="production", session_cookie_secure=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url=URL, session_cookie_samesite="none")
    assert Settings(_env_file=None, database_url=URL, session_cookie_samesite="none", session_cookie_secure=True).session_cookie_samesite == "none"
    for origin in ("*", "https://frontend.invalid/api", "ftp://frontend.invalid", "https://user:secret@frontend.invalid"):
        with pytest.raises(ValidationError):
            Settings(_env_file=None, database_url=URL, cors_origins=origin)


def test_argon2id_phc_and_native_legacy_hashes_remain_secure():
    password = "AdminPass123!"
    encoded = hash_password(password)
    assert encoded.startswith("$argon2id$v=19$m=65536,t=3,p=1$")
    assert verify_password(password, encoded)
    assert not verify_password("WrongPass123!", encoded)
    salt = b"0123456789abcdef"
    digest = hash_secret_raw(password.encode(), salt, time_cost=3, memory_cost=65536, parallelism=1, hash_len=32, type=Type.ID)
    base64url = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
    legacy = f"argon2id${base64url(salt)}${base64url(digest)}"
    assert verify_password(password, legacy)
    assert not verify_password("WrongPass123!", legacy)
    assert not verify_password(password, "malformed")
    assert is_valid_password(password)
    assert not is_valid_password("weak")
    assert digest_token("same token") == digest_token("same token")
    assert len(digest_token("same token")) == 64


def test_limiter_five_failures_expiry_success_and_bounded_storage():
    limiter = LoginRateLimiter(max_buckets=2)
    for _ in range(5):
        assert not limiter.is_limited("one", 100)
        limiter.record_failure("one", 100)
    assert limiter.is_limited("one", 100)
    limiter.record_failure("two", 100)
    assert limiter.is_limited("three", 101)
    assert limiter.cleanup(1000) == 2
    assert not limiter.is_limited("three", 1000)
    for _ in range(5):
        limiter.record_failure("success", 1001)
    limiter.clear("success")
    assert not limiter.is_limited("success", 1001)
