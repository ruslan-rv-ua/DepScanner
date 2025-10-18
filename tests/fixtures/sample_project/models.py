"""Models module."""

import sqlite3
from dataclasses import dataclass


@dataclass
class User:
    """User model."""

    name: str
    email: str


def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    return sqlite3.connect(":memory:")
