"""Tests for version detection."""

import pytest
from pytest_mock import MockerFixture

from depscanner.exceptions import PyPIError
from depscanner.version import (
    compare_versions,
    get_local_version,
    get_package_version,
    get_package_versions,
    get_pypi_version,
)


class TestGetLocalVersion:
    """Tests for get_local_version function."""

    def test_installed_package(self) -> None:
        """Test getting version of an installed package."""
        # pytest should be installed (it's a dev dependency)
        version = get_local_version("pytest")
        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0

    def test_nonexistent_package(self) -> None:
        """Test getting version of a non-existent package."""
        version = get_local_version("nonexistent-package-xyz-123")
        assert version is None

    def test_multiple_packages(self) -> None:
        """Test getting versions of multiple packages."""
        # These should all be installed
        packages = ["pytest", "httpx", "packaging"]

        for package in packages:
            version = get_local_version(package)
            assert version is not None

    def test_exception_handling(self, mocker: MockerFixture) -> None:
        """Test that generic exceptions are handled gracefully."""
        # Mock importlib.metadata.version to raise a generic exception
        mocker.patch(
            "importlib.metadata.version",
            side_effect=RuntimeError("Unexpected error"),
        )

        version = get_local_version("test-package")
        assert version is None


class TestGetPyPIVersion:
    """Tests for get_pypi_version function."""

    def test_popular_package(self, mocker: MockerFixture) -> None:
        """Test getting version from PyPI for a popular package."""
        # Mock httpx.get to avoid actual network calls
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "2.31.0"}}
        mocker.patch("httpx.get", return_value=mock_response)

        version = get_pypi_version("requests")
        assert version == "2.31.0"

    def test_nonexistent_package(self, mocker: MockerFixture) -> None:
        """Test getting version for non-existent package (404)."""
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("httpx.get", return_value=mock_response)

        version = get_pypi_version("nonexistent-package-xyz")
        assert version is None

    def test_pypi_error(self, mocker: MockerFixture) -> None:
        """Test handling PyPI errors (non-404 error codes)."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mocker.patch("httpx.get", return_value=mock_response)

        with pytest.raises(PyPIError) as exc_info:
            get_pypi_version("some-package")

        assert exc_info.value.status_code == 500

    def test_timeout(self, mocker: MockerFixture) -> None:
        """Test handling timeout."""
        import httpx

        mocker.patch("httpx.get", side_effect=httpx.TimeoutException("Timeout"))

        version = get_pypi_version("requests", timeout=1.0)
        assert version is None

    def test_network_error(self, mocker: MockerFixture) -> None:
        """Test handling network errors."""
        import httpx

        mocker.patch("httpx.get", side_effect=httpx.ConnectError("Connection failed"))

        version = get_pypi_version("requests")
        assert version is None

    def test_invalid_json(self, mocker: MockerFixture) -> None:
        """Test handling invalid JSON response."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mocker.patch("httpx.get", return_value=mock_response)

        version = get_pypi_version("requests")
        assert version is None

    def test_missing_version_field(self, mocker: MockerFixture) -> None:
        """Test handling response without version field."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {}}  # No version field
        mocker.patch("httpx.get", return_value=mock_response)

        version = get_pypi_version("requests")
        assert version is None


class TestGetPackageVersion:
    """Tests for get_package_version function."""

    def test_prefer_local_installed(self, mocker: MockerFixture) -> None:
        """Test prefer_local=True with locally installed package."""
        # Mock to ensure we don't hit PyPI
        mock_get = mocker.patch("httpx.get")

        version, source = get_package_version("pytest", prefer_local=True)

        # Should find local version
        assert version is not None
        assert source == "local"

        # Should not call PyPI
        mock_get.assert_not_called()

    def test_prefer_local_not_installed(self, mocker: MockerFixture) -> None:
        """Test prefer_local=True with package not installed locally."""
        # Mock PyPI response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "1.0.0"}}
        mocker.patch("httpx.get", return_value=mock_response)

        version, source = get_package_version("nonexistent-package-xyz", prefer_local=True)

        # Should fallback to PyPI
        assert version == "1.0.0"
        assert source == "pypi"

    def test_prefer_pypi(self, mocker: MockerFixture) -> None:
        """Test prefer_local=False (prefer PyPI)."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "2.0.0"}}
        mocker.patch("httpx.get", return_value=mock_response)

        version, source = get_package_version("pytest", prefer_local=False)

        # Should get PyPI version (even if local is available)
        assert version == "2.0.0"
        assert source == "pypi"

    def test_prefer_pypi_fallback_to_local(self, mocker: MockerFixture) -> None:
        """Test prefer_local=False falls back to local if PyPI fails."""
        # Mock PyPI to return None
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("httpx.get", return_value=mock_response)

        version, source = get_package_version("pytest", prefer_local=False)

        # Should fallback to local version
        assert version is not None
        assert source == "local"

    def test_not_found_anywhere(self, mocker: MockerFixture) -> None:
        """Test package not found locally or on PyPI."""
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("httpx.get", return_value=mock_response)

        version, source = get_package_version("nonexistent-xyz-123")

        assert version is None
        assert source == "unknown"


class TestGetPackageVersions:
    """Tests for get_package_versions function."""

    def test_multiple_packages(self, mocker: MockerFixture) -> None:
        """Test getting versions for multiple packages."""
        # Don't call PyPI for installed packages
        packages = ["pytest", "httpx"]

        results = get_package_versions(packages, prefer_local=True)

        assert len(results) == 2
        assert "pytest" in results
        assert "httpx" in results

        # Both should be found locally
        for package in packages:
            version, source = results[package]
            assert version is not None
            assert source == "local"

    def test_mixed_packages(self, mocker: MockerFixture) -> None:
        """Test mix of installed and non-installed packages."""
        # Mock PyPI for non-existent package
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mocker.patch("httpx.get", return_value=mock_response)

        packages = ["pytest", "nonexistent-xyz"]
        results = get_package_versions(packages, prefer_local=True)

        # pytest should be local
        assert results["pytest"][1] == "local"

        # nonexistent should be unknown
        assert results["nonexistent-xyz"][1] == "unknown"

    def test_empty_list(self) -> None:
        """Test with empty package list."""
        results = get_package_versions([])
        assert results == {}


class TestCompareVersions:
    """Tests for compare_versions function."""

    def test_less_than(self) -> None:
        """Test version1 < version2."""
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("1.0.0", "1.1.0") == -1
        assert compare_versions("1.0.0", "1.0.1") == -1

    def test_greater_than(self) -> None:
        """Test version1 > version2."""
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.1.0", "1.0.0") == 1
        assert compare_versions("1.0.1", "1.0.0") == 1

    def test_equal(self) -> None:
        """Test version1 == version2."""
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("2.3.4", "2.3.4") == 0

    def test_prerelease_versions(self) -> None:
        """Test comparing pre-release versions."""
        assert compare_versions("1.0.0", "1.0.0a1") == 1
        assert compare_versions("1.0.0a1", "1.0.0") == -1
        assert compare_versions("1.0.0a1", "1.0.0b1") == -1

    def test_invalid_versions(self) -> None:
        """Test comparing invalid version strings."""
        # Should fallback to string comparison
        result = compare_versions("invalid", "invalid")
        assert result == 0

        result = compare_versions("aaa", "bbb")
        assert result == -1

    def test_string_comparison_fallback(self, mocker: MockerFixture) -> None:
        """Test that string comparison is used when parsing fails."""
        # Mock parse_version to raise exception
        mocker.patch(
            "depscanner.version.parse_version",
            side_effect=Exception("Parse error"),
        )

        # Should use string comparison
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.0.0", "1.0.0") == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_case_sensitivity_local(self) -> None:
        """Test case sensitivity for local packages."""
        # Package names are case-insensitive in Python
        version1 = get_local_version("pytest")
        version2 = get_local_version("PyTest")

        # Both should return a version (or both None)
        assert (version1 is None) == (version2 is None)

    def test_timeout_parameter(self, mocker: MockerFixture) -> None:
        """Test that timeout parameter is passed correctly."""
        mock_get = mocker.patch("httpx.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "1.0.0"}}
        mock_get.return_value = mock_response

        get_pypi_version("requests", timeout=5.0)

        # Check that timeout was passed
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs.get("timeout") == 5.0
