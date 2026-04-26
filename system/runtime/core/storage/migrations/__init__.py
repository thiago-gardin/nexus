"""Migration entrypoints for the Nexus SQLite bootstrap schema."""

from .bootstrap import apply_migrations

__all__ = ["apply_migrations"]
