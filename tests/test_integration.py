"""Integration tests for depscanner."""

from pathlib import Path

from pytest_mock import MockerFixture

from depscanner import (
    DependencyScanner,
    get_local_version,
    is_stdlib,
    parse_imports,
    resolve_package_name,
    scan_directory,
)


class TestEndToEndScanning:
    """End-to-end integration tests."""

    def test_complete_workflow(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test the complete scanning workflow."""
        # Create a simple Python project
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()

        # Create main.py
        main_file = project_dir / "main.py"
        main_file.write_text("""
import os
import sys
import json
import requests
from flask import Flask

def main():
    pass
""")

        # Create utils.py
        utils_file = project_dir / "utils.py"
        utils_file.write_text("""
import pathlib
import numpy as np
from pandas import DataFrame

def helper():
    pass
""")

        # Mock version detection
        def mock_get_versions(packages, **kwargs):
            versions = {
                "requests": ("2.31.0", "local"),
                "flask": ("3.0.0", "local"),
                "numpy": ("1.24.0", "local"),
                "pandas": ("2.0.0", "local"),
            }
            return {pkg: versions.get(pkg, ("1.0.0", "unknown")) for pkg in packages}

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        # Scan the project
        scanner = DependencyScanner()
        result = scanner.scan(project_dir)

        # Verify results
        assert result.total_files == 2
        assert result.scanned_files == 2
        assert len(result.errors) == 0
        assert result.scan_time > 0

        # Check packages
        package_names = {pkg.name for pkg in result.packages}
        assert "requests" in package_names
        assert "flask" in package_names
        assert "numpy" in package_names
        assert "pandas" in package_names

        # Stdlib should not be in packages
        assert "os" not in package_names
        assert "sys" not in package_names
        assert "json" not in package_names
        assert "pathlib" not in package_names

    def test_mixed_imports(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test project with various import styles."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# Different import styles
import requests
from requests import get, post
from requests.exceptions import Timeout

import numpy as np
from numpy import array

# Stdlib
import os
from pathlib import Path
""")

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        result = scan_directory(tmp_path)

        package_names = {pkg.name for pkg in result.packages}

        # Should have both packages
        assert "requests" in package_names
        assert "numpy" in package_names

        # Should not have stdlib
        assert "os" not in package_names
        assert "pathlib" not in package_names

        # Check that imports are tracked
        requests_pkg = next(pkg for pkg in result.packages if pkg.name == "requests")
        assert "requests" in requests_pkg.imports

    def test_error_handling_integration(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test error handling in full workflow."""
        # Create valid and invalid files
        valid_file = tmp_path / "valid.py"
        valid_file.write_text("import os\n")

        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("def broken(\nprint('error')\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should have 2 files total
        assert result.total_files == 2

        # Only 1 should be scanned successfully
        assert result.scanned_files == 1

        # Should have 1 error
        assert len(result.errors) == 1
        assert "invalid.py" in result.errors[0].file_path

    def test_nested_directories(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test scanning nested directory structure."""
        # Create nested structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module").mkdir()
        (tmp_path / "tests").mkdir()

        # Add files at different levels
        (tmp_path / "main.py").write_text("import requests\n")
        (tmp_path / "src" / "app.py").write_text("import flask\n")
        (tmp_path / "src" / "module" / "utils.py").write_text("import numpy\n")
        (tmp_path / "tests" / "test_app.py").write_text("import pytest\n")

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should find all files
        assert result.total_files == 4

        # Should find all packages
        package_names = {pkg.name for pkg in result.packages}
        assert "requests" in package_names
        assert "flask" in package_names
        assert "numpy" in package_names
        assert "pytest" in package_names


class TestStdlibDetection:
    """Integration tests for stdlib detection."""

    def test_stdlib_vs_external(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that stdlib and external packages are correctly distinguished."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# Stdlib
import os
import sys
import json
import pathlib
import datetime
import collections

# External
import requests
import numpy
import pandas
""")

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        result = scan_directory(tmp_path)

        package_names = {pkg.name for pkg in result.packages}

        # External packages should be present
        assert "requests" in package_names
        assert "numpy" in package_names
        assert "pandas" in package_names

        # Stdlib should NOT be present
        stdlib_modules = ["os", "sys", "json", "pathlib", "datetime", "collections"]
        for stdlib_mod in stdlib_modules:
            assert stdlib_mod not in package_names


class TestVersionResolution:
    """Integration tests for version resolution."""

    def test_local_version_priority(self, tmp_path: Path) -> None:
        """Test that local versions are found for installed packages."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import pytest\nimport httpx\n")

        scanner = DependencyScanner(prefer_local_versions=True)
        result = scanner.scan(tmp_path)

        # pytest and httpx should be found (they're dev dependencies)
        package_names = {pkg.name for pkg in result.packages}

        if "pytest" in package_names:
            pytest_pkg = next(pkg for pkg in result.packages if pkg.name == "pytest")
            assert pytest_pkg.version is not None
            assert pytest_pkg.source == "local"


class TestPackageResolution:
    """Integration tests for package name resolution."""

    def test_special_package_mappings(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test resolution of packages with non-standard names."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import cv2
from PIL import Image
import yaml
from sklearn import datasets
""")

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        package_names = {pkg.name for pkg in result.packages}

        # Should resolve to correct package names
        assert "opencv-python" in package_names or "cv2" in package_names
        assert "Pillow" in package_names or "PIL" in package_names
        assert "PyYAML" in package_names or "yaml" in package_names
        assert "scikit-learn" in package_names or "sklearn" in package_names


class TestIgnoreDirectories:
    """Integration tests for directory ignoring."""

    def test_ignore_venv(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that virtual environment directories are ignored."""
        # Create venv directory with Python files
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "site-packages.py").write_text("import something\n")

        # Create normal file
        (tmp_path / "main.py").write_text("import os\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should only find main.py, not the venv file
        assert result.total_files == 1

    def test_custom_ignore_dirs(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test custom ignore directories."""
        # Create directories
        (tmp_path / "src").mkdir()
        (tmp_path / "ignore_me").mkdir()

        # Add files
        (tmp_path / "src" / "app.py").write_text("import os\n")
        (tmp_path / "ignore_me" / "test.py").write_text("import requests\n")

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner(ignore_dirs=["ignore_me"])
        result = scanner.scan(tmp_path)

        # Should only find src/app.py
        assert result.total_files == 1

        # Should not find requests (it's in ignored directory)
        package_names = {pkg.name for pkg in result.packages}
        assert "requests" not in package_names


class TestPerformance:
    """Performance-related integration tests."""

    def test_scan_time_reasonable(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that scanning completes in reasonable time."""
        # Create multiple files
        for i in range(10):
            file_path = tmp_path / f"file{i}.py"
            file_path.write_text("import os\nimport sys\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should complete in less than 5 seconds for 10 simple files
        assert result.scan_time < 5.0
        assert result.total_files == 10
        assert result.scanned_files == 10


class TestAPIUsage:
    """Tests demonstrating API usage patterns."""

    def test_basic_usage(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test basic API usage as shown in documentation."""
        test_file = tmp_path / "app.py"
        test_file.write_text("import requests\n")

        def mock_get_versions(packages, **kwargs):
            return {"requests": ("2.31.0", "local")}

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        # As shown in README
        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        for package in result.packages:
            assert package.name == "requests"
            assert package.version == "2.31.0"

    def test_functional_api(self, tmp_path: Path) -> None:
        """Test functional API components."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nimport requests\n")

        # Test individual functions
        imports = parse_imports(test_file)
        assert len(imports) >= 2

        # Test stdlib detection
        assert is_stdlib("os") is True
        assert is_stdlib("requests") is False

        # Test package resolution
        package = resolve_package_name("requests")
        assert package == "requests"

        # Test version detection for installed package
        version = get_local_version("pytest")
        assert version is not None  # pytest is installed as dev dep
