"""Models module."""

from dataclasses import dataclass
import sqlite3


@dataclass
class User:
    """User model."""
    name: str
    email: str
