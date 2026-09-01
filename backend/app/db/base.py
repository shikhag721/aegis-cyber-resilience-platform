"""Declarative base for all SQLAlchemy models.

Import every model module in app/models/__init__.py so Alembic's
autogenerate can discover them via Base.metadata.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
