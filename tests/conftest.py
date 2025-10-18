"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_project_dir(fixtures_dir: Path) -> Path:
    """Return the path to the sample project fixture."""
    return fixtures_dir / "sample_project"


@pytest.fixture
def expected_results_dir(fixtures_dir: Path) -> Path:
    """Return the path to expected results directory."""
    return fixtures_dir / "expected_results"
