"""Utility functions."""

import hashlib


def calculate_hash(data: str) -> str:
    """Calculate hash."""
    return hashlib.md5(data.encode()).hexdigest()
