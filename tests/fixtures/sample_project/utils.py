"""Utility functions."""

import hashlib
from datetime import datetime
from typing import Optional


def calculate_hash(data: str) -> str:
    """Calculate hash."""
    return hashlib.md5(data.encode()).hexdigest()


def get_timestamp() -> str:
    """Get current timestamp."""
    return datetime.now().isoformat()
