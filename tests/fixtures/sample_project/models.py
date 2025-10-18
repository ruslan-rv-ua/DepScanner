"""Models module."""

from dataclasses import dataclass


@dataclass
class User:
    """User model."""

    name: str
    email: str
