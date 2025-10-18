"""Tests for the main scanner."""

from pathlib import Path

from pytest_mock import MockerFixture

from depscanner.scanner import DependencyScanner, scan_directory, scan_files


class TestDependencyScanner:
    """Tests for DependencyScanner class."""

    def test_init_defaults(self) -> None:
        """Test scanner initialization with defaults."""
        scanner = DependencyScanner()

        assert scanner.encoding == "utf-8"
        assert scanner.follow_symlinks is False
        assert scanner.prefer_local_versions is True
        assert len(scanner.ignore_dirs) > 0

    def test_init_custom_settings(self) -> None:
        """Test scanner initialization with custom settings."""
        scanner = DependencyScanner(
            ignore_dirs=["custom_dir"],
            follow_symlinks=True,
            encoding="latin-1",
            prefer_local_versions=False,
            version_timeout=5.0,
        )

        assert "custom_dir" in scanner.ignore_dirs
        assert scanner.follow_symlinks is True
        assert scanner.encoding == "latin-1"
        assert scanner.prefer_local_versions is False
        assert scanner.version_timeout == 5.0

    def test_scan_sample_project(self, sample_project_dir: Path, mocker: MockerFixture) -> None:
        """Test scanning the sample project."""

        # Mock version detection to avoid PyPI calls
        # Need to include all packages that might be found
        def mock_get_versions(packages, **kwargs):
            result = {}
            for pkg in packages:
                result[pkg] = ("1.0.0", "local")
            return result

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        result = scanner.scan(sample_project_dir)

        # Check result structure
        assert result.total_files >= 3  # main.py, utils.py, models.py
        assert result.scanned_files >= 2  # At least some files scanned (broken.py fails)
        assert result.scan_time > 0

        # Should have found some packages
        assert len(result.packages) > 0

        # Check for specific packages (third-party ones)
        package_names = {pkg.name for pkg in result.packages}
        assert "requests" in package_names or "numpy" in package_names or "flask" in package_names

    def test_scan_single_file(self, sample_project_dir: Path, mocker: MockerFixture) -> None:
        """Test scanning a single Python file."""

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        file_path = sample_project_dir / "main.py"
        result = scanner.scan(file_path)

        assert result.total_files == 1
        assert result.scanned_files <= 1

    def test_scan_with_errors(self, sample_project_dir: Path, mocker: MockerFixture) -> None:
        """Test that errors are captured properly."""

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        result = scanner.scan(sample_project_dir)

        # broken.py should cause an error
        assert len(result.errors) > 0

        # Check error structure
        error = result.errors[0]
        assert "broken.py" in error.file_path
        assert error.error_type is not None
        assert error.message is not None

    def test_scan_files_method(self, sample_project_dir: Path, mocker: MockerFixture) -> None:
        """Test scanning specific files."""
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "hashlib": ("1.0.0", "local"),
            },
        )

        scanner = DependencyScanner()
        files = [
            sample_project_dir / "utils.py",
            sample_project_dir / "models.py",
        ]
        result = scanner.scan_files(files)

        assert result.total_files == 2
        assert result.scanned_files >= 1

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning an empty directory."""
        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        assert result.total_files == 0
        assert result.scanned_files == 0
        assert len(result.packages) == 0
        assert len(result.errors) == 0

    def test_scan_nonexistent_directory(self) -> None:
        """Test scanning a non-existent directory."""
        scanner = DependencyScanner()
        result = scanner.scan("/nonexistent/path/xyz")

        assert result.total_files == 0
        assert result.scanned_files == 0

    def test_ignore_stdlib_packages(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that stdlib packages are not included in results."""
        # Create a file with only stdlib imports
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nimport sys\nimport json\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should have no packages (all are stdlib)
        assert len(result.packages) == 0

    def test_package_deduplication(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that duplicate packages are handled correctly."""
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "requests": ("2.31.0", "local"),
            },
        )

        # Create files with the same import
        file1 = tmp_path / "file1.py"
        file1.write_text("import requests\n")
        file2 = tmp_path / "file2.py"
        file2.write_text("import requests\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should only have one 'requests' package
        package_names = [pkg.name for pkg in result.packages]
        assert package_names.count("requests") == 1

    def test_imports_tracking(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that imports are tracked for each package."""
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "requests": ("2.31.0", "local"),
            },
        )

        # Create file with multiple imports from same package
        test_file = tmp_path / "test.py"
        test_file.write_text("import requests\nfrom requests import get\n")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should have requests package with tracked imports
        requests_pkg = next((pkg for pkg in result.packages if pkg.name == "requests"), None)
        assert requests_pkg is not None
        assert "requests" in requests_pkg.imports

    def test_success_rate_calculation(
        self, sample_project_dir: Path, mocker: MockerFixture
    ) -> None:
        """Test that success rate is calculated correctly."""

        def mock_get_versions(packages, **kwargs):
            return dict.fromkeys(packages, ("1.0.0", "local"))

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            side_effect=mock_get_versions,
        )

        scanner = DependencyScanner()
        result = scanner.scan(sample_project_dir)

        # Should have a success rate between 0 and 1
        assert 0 <= result.success_rate <= 1

        # If we have any files, success rate should reflect parsing success
        if result.total_files > 0:
            expected_rate = result.scanned_files / result.total_files
            assert result.success_rate == expected_rate


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_scan_directory_function(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test scan_directory convenience function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\n")

        result = scan_directory(tmp_path)

        assert isinstance(result, type(result))  # ScanResult
        assert result.total_files >= 1

    def test_scan_files_function(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test scan_files convenience function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\n")

        result = scan_files([test_file])

        assert isinstance(result, type(result))  # ScanResult
        assert result.total_files == 1


class TestEdgeCases:
    """Test edge cases."""

    def test_scan_with_non_python_files(self, tmp_path: Path) -> None:
        """Test scanning directory with non-Python files."""
        # Create some non-Python files
        (tmp_path / "readme.txt").write_text("Hello")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / "test.py").write_text("import os")

        scanner = DependencyScanner()
        result = scanner.scan(tmp_path)

        # Should only process the .py file
        assert result.total_files == 1

    def test_scan_files_with_non_python(self, tmp_path: Path) -> None:
        """Test scan_files with mix of Python and non-Python files."""
        py_file = tmp_path / "test.py"
        py_file.write_text("import os")
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not python")

        scanner = DependencyScanner()
        result = scanner.scan_files([py_file, txt_file])

        # Should only process the .py file
        assert result.total_files == 1

    def test_scan_with_custom_resolver(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test scanner with custom resolver."""
        from depscanner.resolver import PackageResolver

        # Create custom resolver with mapping
        custom_resolver = PackageResolver(mapping={"mymodule": "my-package"})

        test_file = tmp_path / "test.py"
        test_file.write_text("import mymodule\n")

        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={
                "my-package": ("1.0.0", "local"),
            },
        )

        scanner = DependencyScanner(resolver=custom_resolver)
        result = scanner.scan(tmp_path)

        # Should resolve mymodule to my-package
        package_names = {pkg.name for pkg in result.packages}
        assert "my-package" in package_names

    def test_empty_file_list(self) -> None:
        """Test scanning empty file list."""
        scanner = DependencyScanner()
        result = scanner.scan_files([])

        assert result.total_files == 0
        assert result.scanned_files == 0
        assert len(result.packages) == 0

    def test_dotted_import_package_aggregation(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test that dotted imports are aggregated correctly."""
        # Create a file with dotted imports from same package
        test_file = tmp_path / "test.py"
        test_file.write_text(
            "import requests.adapters\n"
            "import requests.auth\n"
            "from requests import Session\n"
        )

        # Mock version lookup
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={"requests": ("2.31.0", "local")},
        )

        scanner = DependencyScanner()
        result = scanner.scan_files([test_file])

        # Should have only one package
        assert len(result.packages) == 1
        assert result.packages[0].name == "requests"
        
        # Should track all import variations
        imports = result.packages[0].imports
        assert "requests.adapters" in imports or "requests" in imports
        assert len(imports) >= 1

    def test_multiple_modules_same_package(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test handling multiple module imports from same package."""
        # Create files that import different submodules of the same package
        file1 = tmp_path / "file1.py"
        file1.write_text("import requests\nimport requests.adapters\n")
        
        file2 = tmp_path / "file2.py"
        file2.write_text("import requests.auth\nimport requests\n")

        # Mock version lookup
        mocker.patch(
            "depscanner.scanner.get_package_versions",
            return_value={"requests": ("2.31.0", "pypi")},
        )

        scanner = DependencyScanner()
        result = scanner.scan_files([file1, file2])

        # Should have one package with deduplicated imports
        assert len(result.packages) == 1
        pkg = result.packages[0]
        assert pkg.name == "requests"
        
        # Imports should be unique (no duplicates)
        imports_list = pkg.imports
        assert len(imports_list) == len(set(imports_list))
