"""Import every model module here so Base.metadata (and Alembic
autogenerate) can discover all tables from a single import.
"""
from app.models.user import User  # noqa: F401
