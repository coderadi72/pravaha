"""Alembic obtains connection configuration from the same API settings."""
from logging.config import fileConfig

from alembic import context

from backend.app.db.base import Base
from backend.app.db.session import create_engine_and_factory
from backend.app import models  # noqa: F401 - register shared metadata

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)
target_metadata = Base.metadata


def run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    from backend.app.core.config import Settings
    settings = Settings()
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied = config.attributes.get("connection")
    if supplied is not None:
        run_migrations(supplied)
    else:
        from backend.app.core.config import Settings
        engine, _ = create_engine_and_factory(Settings())
        try:
            with engine.connect() as connection:
                run_migrations(connection)
        finally:
            engine.dispose()
