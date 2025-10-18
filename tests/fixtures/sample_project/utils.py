"""Utility functions."""

import hashlib
from datetime import datetime
import typing


def calculate_hash(data: str) -> str:
    """Calculate hash."""
    return hashlib.md5(data.encode()).hexdigest()
