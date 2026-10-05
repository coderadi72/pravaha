"""PostgreSQL engine/session construction shared by API, migrations and scripts."""
import re
from typing import Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


class DatabaseSettings(Protocol):
    database_url: str
    db_schema: str | None
    sql_echo: bool


def create_engine_and_factory(settings: DatabaseSettings):
    url = make_url(settings.database_url)
    if url.get_backend_name() != "postgresql":
        raise ValueError("DATABASE_URL must use PostgreSQL; SQLite is legacy import data only.")
    schema = settings.db_schema
    if schema and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise ValueError("DB_SCHEMA must be a valid PostgreSQL schema identifier.")
    options = {"options": f"-csearch_path={schema}"} if schema else {}
    options.update(connect_timeout=getattr(settings,"db_connect_timeout",10), prepare_threshold=None)
    pooling = {"poolclass":NullPool} if getattr(settings,"db_pool_mode","queue")=="null" else {
        "pool_size":getattr(settings,"db_pool_size",5),"max_overflow":getattr(settings,"db_max_overflow",5),
        "pool_timeout":getattr(settings,"db_pool_timeout",30),"pool_recycle":getattr(settings,"db_pool_recycle",1800)}
    engine = create_engine(url, echo=settings.sql_echo, pool_pre_ping=True, connect_args=options, **pooling)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine, factory
