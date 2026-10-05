"""Shared SQLAlchemy metadata; tables are installed only through Alembic."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
