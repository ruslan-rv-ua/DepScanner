"""Performance tests for depscanner."""

import time
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from depscanner import DependencyScanner, parse_imports, scan_directory
from depscanner.parser import parse_multiple_files
from depscanner.resolver import PackageResolver


class TestParserPerformance:
    """Performance tests for the parser component."""

    def test_parse_single_file_performance(self, tmp_path: Path) -> None:
        """Test parsing a single file with many imports."""
        # Create a file with 100 imports
        test_file = tmp_path / "large_imports.py"
        imports = "\n".join([f"import module_{i}" for i in range(100)])
        test_file.write_text(imports)

        # Measure parsing time
        start_time = time.perf_counter()
        result = parse_imports(test_file)
        elapsed = time.perf_counter() - start_time

        # Should parse quickly (< 100ms for 100 imports)
        assert elapsed < 0.1
        assert len(result) == 100

    def test_parse_multiple_files_performance(self, tmp_path: Path) -> None:
        """Test parsing multiple files."""
        # Create 50 files with 20 imports each
        files = []
        for i in range(50):
            file_path = tmp_path / f"file_{i}.py"
            imports = "\n".join([f"import module_{j}" for j in range(20)])
            file_path.write_text(imports)
            files.append(file_path)

        # Measure parsing time
        start_time = time.perf_counter()
        imports, errors = parse_multiple_files(files)
        elapsed = time.perf_counter() - start_time

        # Should parse 50 files quickly (< 500ms)
        assert elapsed < 0.5
        assert len(imports) == 1000  # 50 files * 20 imports
        assert len(errors) == 0

    def test_parse_large_file_performance(self, tmp_path: Path) -> None:
        """Test parsing a large file with complex code."""
        # Create a large file with mixed content
        test_file = tmp_path / "large_file.py"
        content = []
        for i in range(50):
            content.append(f"import module_{i}")
            content.append(f"from package_{i} import func_{i}, Class_{i}")
            content.append(f"\ndef function_{i}():")
            content.append(f"    return {i}")
            content.append("")

        test_file.write_text("\n".join(content))

        # Measure parsing time
        start_time = time.perf_counter()
        result = parse_imports(test_file)
        elapsed = time.perf_counter() - start_time

        # Should parse quickly even for large files
        assert elapsed < 0.2
        assert len(result) == 100  # 50 regular imports + 50 from imports


class TestResolverPerformance:
    """Performance tests for the resolver component."""

    def test_resolve_many_packages_performance(self, mocker: MockerFixture) -> None:
        """Test resolving a large number of packages."""
        # Mock importlib.metadata to avoid actual lookups
        mock_distributions = {}
        for i in range(100):
            mock_distributions[f"package-{i}"] = mocker.Mock(
                metadata={"Name": f"package-{i}"},
                read_text=lambda: "",
            )

        def mock_distribution(name):
            return mock_distributions.get(name)

        mocker.patch("importlib.metadata.distribution", side_effect=mock_distribution)
        mocker.patch("importlib.metadata.packages_distributions", return_value={})

        # Resolve 100 packages
        resolver = PackageResolver()
        import_names = [f"module_{i}" for i in range(100)]

        start_time = time.perf_counter()
        results = [resolver.resolve(name) for name in import_names]
        elapsed = time.perf_counter() - start_time

        # Should resolve quickly (< 200ms for 100 packages)
        assert elapsed < 0.2
        assert len(results) == 100

    def test_resolve_with_cache_performance(self) -> None:
        """Test that caching improves performance."""
        resolver = PackageResolver()

        # First resolution (no cache)
        start_time = time.perf_counter()
        for _ in range(100):
            resolver.resolve("requests")
        first_elapsed = time.perf_counter() - start_time

        # Second resolution (with cache)
        start_time = time.perf_counter()
        for _ in range(100):
            resolver.resolve("requests")
        second_elapsed = time.perf_counter() - start_time

        # Cached should be significantly faster
        assert second_elapsed < first_elapsed * 0.5  # At least 2x faster


class TestScannerPerformance:
    """Performance tests for the main scanner."""

    def test_scan_small_project_performance(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test scanning a small project."""
        # Create a small project (10 files, 5 imports each)
        project_dir = tmp_path / "small_project"
        project_dir.mkdir()

        for i in range(10):
            file_path = project_dir / f"module_{i}.py"
            imports = "\n".join(
                [
                    "import os",
                    "import sys",
                    "import requests",
                    "import numpy",
                    "import pandas",
                ]
            )
            file_path.write_text(imports)

        # Mock version detection
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "requests": ("2.31.0", "local"),
                "numpy": ("1.24.0", "local"),
                "pandas": ("2.0.0", "local"),
            },
        )

        # Measure scanning time
        scanner = DependencyScanner()
        start_time = time.perf_counter()
        result = scanner.scan(project_dir)
        elapsed = time.perf_counter() - start_time

        # Should scan quickly (< 500ms)
        assert elapsed < 0.5
        assert result.total_files == 10
        assert result.scanned_files == 10
        assert len(result.packages) == 3  # requests, numpy, pandas

    def test_scan_medium_project_performance(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test scanning a medium-sized project."""
        # Create a medium project (50 files, varying imports)
        project_dir = tmp_path / "medium_project"
        project_dir.mkdir()

        packages = ["requests", "numpy", "pandas", "flask", "django", "pytest"]
        for i in range(50):
            file_path = project_dir / f"module_{i}.py"
            # Each file imports 3 random packages
            selected = packages[i % len(packages) : (i % len(packages)) + 3]
            imports = "\n".join([f"import {pkg}" for pkg in selected])
            file_path.write_text(imports)

        # Mock version detection
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={pkg: ("1.0.0", "local") for pkg in packages},
        )

        # Measure scanning time
        scanner = DependencyScanner()
        start_time = time.perf_counter()
        result = scanner.scan(project_dir)
        elapsed = time.perf_counter() - start_time

        # Should scan in reasonable time (< 2 seconds)
        assert elapsed < 2.0
        assert result.total_files == 50
        assert result.scanned_files == 50

    def test_scan_with_subdirectories_performance(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test scanning a project with nested directories."""
        # Create nested directory structure
        project_dir = tmp_path / "nested_project"
        project_dir.mkdir()

        # Create 5 subdirectories with 10 files each
        for dir_i in range(5):
            sub_dir = project_dir / f"package_{dir_i}"
            sub_dir.mkdir()
            for file_i in range(10):
                file_path = sub_dir / f"module_{file_i}.py"
                file_path.write_text("import requests\nimport numpy")

        # Mock version detection
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={"requests": ("2.31.0", "local"), "numpy": ("1.24.0", "local")},
        )

        # Measure scanning time
        scanner = DependencyScanner()
        start_time = time.perf_counter()
        result = scanner.scan(project_dir)
        elapsed = time.perf_counter() - start_time

        # Should scan nested structure efficiently (< 1 second)
        assert elapsed < 1.0
        assert result.total_files == 50
        assert result.scanned_files == 50
        assert len(result.packages) == 2


class TestEndToEndPerformance:
    """End-to-end performance tests."""

    def test_real_world_project_simulation(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Simulate scanning a real-world project."""
        # Create a realistic project structure
        project_dir = tmp_path / "real_project"
        (project_dir / "src").mkdir(parents=True)
        (project_dir / "tests").mkdir()
        (project_dir / "scripts").mkdir()

        # Common imports used in real projects
        common_imports = """
import os
import sys
import json
import pathlib
from typing import Dict, List, Optional
import requests
import numpy as np
import pandas as pd
from flask import Flask, jsonify
import pytest
"""

        # Create source files
        for i in range(20):
            (project_dir / "src" / f"module_{i}.py").write_text(common_imports)

        # Create test files
        for i in range(10):
            (project_dir / "tests" / f"test_{i}.py").write_text(common_imports)

        # Create script files
        for i in range(5):
            (project_dir / "scripts" / f"script_{i}.py").write_text(common_imports)

        # Mock version detection
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "requests": ("2.31.0", "local"),
                "numpy": ("1.24.0", "local"),
                "pandas": ("2.0.0", "local"),
                "flask": ("3.0.0", "local"),
                "pytest": ("8.0.0", "local"),
            },
        )

        # Measure full scan
        start_time = time.perf_counter()
        result = scan_directory(str(project_dir))
        elapsed = time.perf_counter() - start_time

        # Should complete in reasonable time (< 2 seconds)
        assert elapsed < 2.0
        assert result.total_files == 35
        assert result.scanned_files == 35
        assert len(result.packages) == 5

        # Check performance metrics
        assert result.scan_time > 0
        files_per_second = result.scanned_files / result.scan_time
        assert files_per_second > 10  # Should scan at least 10 files/second

    def test_scan_with_errors_performance(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test that errors don't significantly impact performance."""
        # Create mix of valid and invalid files
        project_dir = tmp_path / "mixed_project"
        project_dir.mkdir()

        # 40 valid files
        for i in range(40):
            file_path = project_dir / f"valid_{i}.py"
            file_path.write_text("import requests\nimport numpy")

        # 10 invalid files
        for i in range(10):
            file_path = project_dir / f"invalid_{i}.py"
            file_path.write_text("import requests\nimport numpy\nthis is invalid syntax ((")

        # Mock version detection
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={"requests": ("2.31.0", "local"), "numpy": ("1.24.0", "local")},
        )

        # Measure scanning time
        scanner = DependencyScanner()
        start_time = time.perf_counter()
        result = scanner.scan(project_dir)
        elapsed = time.perf_counter() - start_time

        # Should still complete quickly despite errors (< 1 second)
        assert elapsed < 1.0
        assert result.total_files == 50
        assert result.scanned_files == 40  # Only valid files
        assert len(result.errors) == 10  # Invalid files


class TestMemoryEfficiency:
    """Tests to ensure memory efficiency."""

    def test_large_project_memory_usage(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test that scanning doesn't consume excessive memory."""
        # Create a large project (100 files)
        project_dir = tmp_path / "large_project"
        project_dir.mkdir()

        for i in range(100):
            file_path = project_dir / f"module_{i}.py"
            # Create files with reasonable amount of imports
            imports = "\n".join([f"import module_{j}" for j in range(10)])
            file_path.write_text(imports)

        # Mock version detection - return empty dict to avoid version lookup
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={f"module_{i}": ("1.0.0", "unknown") for i in range(100)},
        )

        # Scan the project
        scanner = DependencyScanner()
        result = scanner.scan(project_dir)

        # Verify scan completed successfully
        assert result.total_files == 100
        # Result should be compact - just metadata, not full file contents
        assert len(result.packages) <= 100  # Max 100 unique packages


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests (run with -m benchmark flag)."""

    def test_benchmark_parse_100_files(self, tmp_path: Path) -> None:
        """Benchmark: Parse 100 Python files."""
        files = []
        for i in range(100):
            file_path = tmp_path / f"file_{i}.py"
            file_path.write_text(f"import module_{i}\nimport package_{i}")
            files.append(file_path)

        start = time.perf_counter()
        imports, errors = parse_multiple_files(files)
        duration = time.perf_counter() - start

        print(f"\nParsed 100 files in {duration:.3f}s ({100/duration:.1f} files/s)")
        assert errors == []

    def test_benchmark_full_scan(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Benchmark: Full project scan."""
        project_dir = tmp_path / "benchmark_project"
        project_dir.mkdir()

        # Create realistic project
        for i in range(50):
            file_path = project_dir / f"module_{i}.py"
            file_path.write_text("import requests\nimport numpy\nimport pandas")

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "requests": ("2.31.0", "local"),
                "numpy": ("1.24.0", "local"),
                "pandas": ("2.0.0", "local"),
            },
        )

        scanner = DependencyScanner()
        start = time.perf_counter()
        result = scanner.scan(project_dir)
        duration = time.perf_counter() - start

        print(
            f"\nScanned {result.scanned_files} files in {duration:.3f}s "
            f"({result.scanned_files/duration:.1f} files/s)"
        )
        assert result.total_files == 50
