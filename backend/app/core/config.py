"""Environment-only runtime configuration; PostgreSQL is mandatory."""
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", ROOT / "backend" / ".env"),
        env_file_encoding="utf-8", extra="ignore", case_sensitive=False,
    )
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = Field(repr=False)
    db_schema: str = "public"
    intelligence_stale_days: int = Field(default=7, ge=1, le=365)
    intelligence_finish_window_days: int = Field(default=3, ge=1, le=90)
    intelligence_min_progress: int = Field(default=80, ge=1, le=100)
    intelligence_high_delay_days: int = Field(default=7, ge=1, le=365)
    intelligence_incomplete_threshold: int = Field(default=3, ge=2, le=100)
    db_pool_size: int = Field(default=5, ge=1, le=50)
    db_max_overflow: int = Field(default=5, ge=0, le=50)
    db_pool_timeout: int = Field(default=30, ge=1, le=120)
    db_pool_recycle: int = Field(default=1800, ge=60, le=86400)
    db_pool_mode: Literal["queue", "null"] = "queue"
    db_connect_timeout: int = Field(default=10, ge=1, le=60)
    rate_limit_backend: Literal["memory", "postgresql"] = "memory"
    login_max_attempts: int = Field(default=5, ge=1, le=100)
    login_window_seconds: int = Field(default=900, ge=1, le=86400)
    login_max_buckets: int = Field(default=10000, ge=100, le=1_000_000)
    signup_max_attempts: int = Field(default=5, ge=1, le=100)
    signup_window_seconds: int = Field(default=900, ge=1, le=86400)
    signup_max_buckets: int = Field(default=10000, ge=100, le=1_000_000)
    registration_review_organization_id: str = Field(default="", max_length=120)
    session_ttl_seconds: int = Field(default=28800, ge=300, le=604800)
    request_body_limit_bytes: int = Field(default=1_048_576, ge=1024, le=64 * 1024 * 1024)
    request_upload_body_limit_bytes: int = Field(default=8_388_608, ge=1024, le=64 * 1024 * 1024)
    attachment_max_bytes: int = Field(default=5_242_880, ge=1, le=64 * 1024 * 1024)
    image_max_pixels: int = Field(default=20_000_000, ge=1, le=200_000_000)
    xlsx_max_entries: int = Field(default=1000, ge=1, le=100_000)
    xlsx_max_uncompressed_bytes: int = Field(default=41_943_040, ge=1, le=512 * 1024 * 1024)
    xlsx_max_compression_ratio: int = Field(default=300, ge=1, le=10_000)
    schedule_max_rows: int = Field(default=2000, ge=1, le=1_000_000)
    schedule_max_columns: int = Field(default=60, ge=1, le=1000)
    schedule_max_relationships: int = Field(default=10000, ge=1, le=1_000_000)
    dependency_cell_max_count: int = Field(default=50, ge=1, le=1000)
    dependency_max_lag_days: float = Field(default=3650, gt=0, le=100_000)
    intelligence_max_input_rows: int = Field(default=10000, ge=1, le=1_000_000)
    ocr_provider: str = "none"
    asr_provider: str = "none"
    ai_provider: str = "none"
    ai_api_key: str = Field(default="", repr=False)
    ai_model: str = ""
    ai_base_url: str = ""
    ai_provider_order: Annotated[list[str], NoDecode] = ["groq", "nvidia"]
    groq_api_key: str = Field(default="", repr=False)
    groq_model: str = "openai/gpt-oss-20b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_reasoning_effort: Literal["low", "medium", "high"] | None = None
    nvidia_api_key: str = Field(default="", repr=False)
    nvidia_model: str = "nvidia/nemotron-3-super-120b-a12b"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_max_output_tokens: int = Field(default=4096, ge=100, le=32768)
    nvidia_reasoning_effort: Literal["none", "low", "high", "max"] | None = None
    ai_response_format: Literal["text", "json_object"] = "text"
    ai_fallback_enabled: bool = True
    ai_default_language: str = "en"
    ai_supported_languages: Annotated[list[str], NoDecode] = ["en", "hi", "hi-Latn"]
    ai_request_timeout_seconds: int = Field(default=30, ge=1, le=120)
    ai_max_retries: int = Field(default=0, ge=0, le=2)
    ai_max_tool_calls: int = Field(default=3, ge=1, le=10)
    ai_max_context_chars: int = Field(default=24000, ge=4000, le=100000)
    ai_max_input_tokens: int = Field(default=3000, ge=1500, le=25000)
    ai_max_output_tokens: int = Field(default=500, ge=100, le=8000)
    ai_max_response_bytes: int = Field(default=131072, ge=4096, le=1048576)
    ai_cooldown_seconds: int = Field(default=60, ge=1, le=86400)
    ai_daily_request_budget: int = Field(default=0, ge=0, le=100000)
    assistant_question_chars: int = Field(default=1200, ge=50, le=4000)
    assistant_history_questions: int = Field(default=8, ge=0, le=10)
    assistant_record_limit: int = Field(default=12, ge=1, le=50)
    assistant_excerpt_chars: int = Field(default=300, ge=50, le=1000)
    assistant_conversation_ttl_seconds: int = Field(default=1800, ge=60, le=28800)
    assistant_max_requests: int = Field(default=4, ge=1, le=100)
    assistant_window_seconds: int = Field(default=60, ge=1, le=86400)
    assistant_max_requests_per_session: int = Field(default=20, ge=1, le=1000)
    assistant_max_concurrent: int = Field(default=2, ge=1, le=20)
    ocr_api_key: str = Field(default="", repr=False)
    asr_api_key: str = Field(default="", repr=False)
    trusted_proxy_ips: str = "127.0.0.1"
    sql_echo: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: Annotated[list[str], NoDecode] = []
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    session_cookie_secure: bool | None = None
    enable_api_docs: bool | None = None
    seed_admin_email: str = ""
    seed_admin_password: str = Field(default="", repr=False)
    seed_pm_email: str = ""
    seed_pm_password: str = Field(default="", repr=False)
    seed_tl_email: str = ""
    seed_tl_password: str = Field(default="", repr=False)

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value):
        value = value.strip()
        if value.startswith("postgres://"):
            value = "postgresql+psycopg://" + value[len("postgres://"):]
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value[len("postgresql://"):]
        try:
            parsed = make_url(value)
        except Exception as exc:
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL.") from exc
        if parsed.drivername != "postgresql+psycopg" or not parsed.database or not parsed.host:
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")
        return value

    @field_validator("db_schema")
    @classmethod
    def safe_schema(cls, value):
        import re
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError("DB_SCHEMA must be a valid SQL identifier.")
        return value

    @field_validator("ai_provider_order", "ai_supported_languages", mode="before")
    @classmethod
    def assistant_lists(cls, value):
        return [v.strip() for v in value.split(",") if v.strip()] if isinstance(value, str) else value

    @model_validator(mode="after")
    def assistant_config(self):
        self.ai_provider = self.ai_provider.strip().lower()
        if self.ai_provider not in {"none", "auto", "groq", "nvidia", "openai"}:
            raise ValueError("AI_PROVIDER must be none, auto, groq or nvidia (openai is retained but unavailable).")
        if not self.ai_provider_order or len(set(self.ai_provider_order)) != len(self.ai_provider_order) or any(p not in {"groq", "nvidia"} for p in self.ai_provider_order):
            raise ValueError("AI_PROVIDER_ORDER must contain unique groq/nvidia entries.")
        if not self.ai_supported_languages or any(p not in {"en", "hi", "hi-Latn"} for p in self.ai_supported_languages) or self.ai_default_language not in self.ai_supported_languages:
            raise ValueError("AI languages require installed catalogues en, hi, hi-Latn and an enabled default.")
        for value in (self.groq_base_url, self.nvidia_base_url, self.ai_base_url):
            if not value:
                continue
            url = urlsplit(value)
            if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
                raise ValueError("AI base URLs must be operator-configured HTTPS endpoints without credentials/query/fragment.")
        return self

    @field_validator("cors_origins", mode="before")
    @classmethod
    def origin_list(cls, value):
        origins = [item.strip().rstrip("/") for item in value.split(",") if item.strip()] if isinstance(value, str) else value
        for origin in origins:
            parsed = urlsplit(origin)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
                raise ValueError("CORS_ORIGINS must contain complete HTTP origins without paths or wildcards.")
        return origins

    @model_validator(mode="after")
    def safe_cookies(self):
        if self.session_cookie_secure is None:
            self.session_cookie_secure = self.app_env == "production"
        if self.app_env == "production" and not self.session_cookie_secure:
            raise ValueError("Production session cookies must be Secure.")
        if self.session_cookie_samesite == "none" and not self.session_cookie_secure:
            raise ValueError("SameSite=None requires Secure session cookies.")
        if self.enable_api_docs is None:
            self.enable_api_docs = self.app_env != "production"
        if self.app_env == "production":
            if make_url(self.database_url).query.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
                raise ValueError("Production PostgreSQL must require SSL in DATABASE_URL.")
            if self.rate_limit_backend != "postgresql":
                raise ValueError("Production requires the shared PostgreSQL rate limiter.")
            if self.sql_echo or not self.cors_origins or any(not origin.startswith("https://") for origin in self.cors_origins):
                raise ValueError("Production requires exact HTTPS CORS origins and disabled SQL echo.")
        return self


@lru_cache
def get_settings():
    return Settings()
