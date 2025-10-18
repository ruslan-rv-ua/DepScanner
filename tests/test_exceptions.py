"""Tests for custom exceptions."""

import pytest

from depscanner.exceptions import (
    DepScannerError,
    FileParsingError,
    InvalidPythonFileError,
    PackageResolutionError,
    PyPIError,
    VersionDetectionError,
)


class TestDepScannerError:
    """Tests for DepScannerError base exception."""

    def test_base_exception(self) -> None:
        """Test that DepScannerError can be raised."""
        with pytest.raises(DepScannerError):
            raise DepScannerError("Test error")


class TestFileParsingError:
    """Tests for FileParsingError."""

    def test_file_parsing_error(self) -> None:
        """Test FileParsingError creation and attributes."""
        original = SyntaxError("invalid syntax")
        error = FileParsingError("/path/to/file.py", original)

        assert error.file_path == "/path/to/file.py"
        assert error.original_error is original
        assert "Failed to parse /path/to/file.py" in str(error)
        assert "invalid syntax" in str(error)


class TestInvalidPythonFileError:
    """Tests for InvalidPythonFileError."""

    def test_invalid_python_file_error(self) -> None:
        """Test InvalidPythonFileError creation and attributes."""
        error = InvalidPythonFileError("/path/to/file.txt")

        assert error.file_path == "/path/to/file.txt"
        assert "Not a valid Python file" in str(error)
        assert "/path/to/file.txt" in str(error)


class TestPackageResolutionError:
    """Tests for PackageResolutionError."""

    def test_package_resolution_error(self) -> None:
        """Test PackageResolutionError creation and attributes."""
        error = PackageResolutionError("sklearn", "Package not found in mapping")

        assert error.module_name == "sklearn"
        assert error.reason == "Package not found in mapping"
        assert "Failed to resolve package for module 'sklearn'" in str(error)
        assert "Package not found in mapping" in str(error)


class TestVersionDetectionError:
    """Tests for VersionDetectionError."""

    def test_version_detection_error(self) -> None:
        """Test VersionDetectionError creation and attributes."""
        error = VersionDetectionError("my-package", "Network timeout")

        assert error.package_name == "my-package"
        assert error.reason == "Network timeout"
        assert "Failed to detect version for 'my-package'" in str(error)
        assert "Network timeout" in str(error)


class TestPyPIError:
    """Tests for PyPIError."""

    def test_pypi_error(self) -> None:
        """Test PyPIError creation."""
        error = PyPIError("Connection failed")

        assert "Connection failed" in str(error)
        assert isinstance(error, DepScannerError)
