"""Audit service boundary; events participate in the caller's transaction."""
from backend.app.db.repository import append_audit

__all__ = ["append_audit"]
