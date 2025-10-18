"""Tests for data models."""

import pytest

from depscanner.models import ImportInfo, PackageInfo, ScanError, ScanResult


class TestImportInfo:
    """Tests for ImportInfo model."""
    
    def test_create_import_info(self) -> None:
        """Test creating ImportInfo instance."""
        import_info = ImportInfo(
            module_name="requests",
            package_name="requests",
            is_stdlib=False,
            file_path="/path/to/file.py",
            line_number=1,
        )
        
        assert import_info.module_name == "requests"
        assert import_info.package_name == "requests"
        assert import_info.is_stdlib is False
        assert import_info.file_path == "/path/to/file.py"
        assert import_info.line_number == 1
    
    def test_import_info_is_frozen(self) -> None:
        """Test that ImportInfo is immutable."""
        import_info = ImportInfo(
            module_name="test",
            package_name="test",
            is_stdlib=False,
            file_path="test.py",
            line_number=1,
        )
        
        with pytest.raises(AttributeError):
            import_info.module_name = "changed"  # type: ignore


class TestPackageInfo:
    """Tests for PackageInfo model."""
    
    def test_create_package_info(self) -> None:
        """Test creating PackageInfo instance."""
        pkg = PackageInfo(
            name="requests",
            version="2.31.0",
            source="local",
            imports=["requests"],
        )
        
        assert pkg.name == "requests"
        assert pkg.version == "2.31.0"
        assert pkg.source == "local"
        assert pkg.imports == ["requests"]
    
    def test_package_info_defaults(self) -> None:
        """Test PackageInfo default values."""
        pkg = PackageInfo(name="test")
        
        assert pkg.version is None
        assert pkg.source == "unknown"
        assert pkg.imports == []
    
    def test_package_equality(self) -> None:
        """Test that packages are equal if names match (case-insensitive)."""
        pkg1 = PackageInfo(name="Requests", version="1.0")
        pkg2 = PackageInfo(name="requests", version="2.0")
        pkg3 = PackageInfo(name="flask", version="1.0")
        
        assert pkg1 == pkg2
        assert pkg1 != pkg3
    
    def test_package_hash(self) -> None:
        """Test that packages can be used in sets."""
        pkg1 = PackageInfo(name="Requests")
        pkg2 = PackageInfo(name="requests")
        pkg3 = PackageInfo(name="Flask")
        
        packages = {pkg1, pkg2, pkg3}
        assert len(packages) == 2  # Requests and Flask


class TestScanError:
    """Tests for ScanError model."""
    
    def test_create_scan_error(self) -> None:
        """Test creating ScanError instance."""
        error = ScanError(
            file_path="/path/to/file.py",
            error_type="SyntaxError",
            message="Invalid syntax",
            line_number=10,
        )
        
        assert error.file_path == "/path/to/file.py"
        assert error.error_type == "SyntaxError"
        assert error.message == "Invalid syntax"
        assert error.line_number == 10
    
    def test_scan_error_no_line_number(self) -> None:
        """Test ScanError without line number."""
        error = ScanError(
            file_path="test.py",
            error_type="IOError",
            message="File not found",
        )
        
        assert error.line_number is None


class TestScanResult:
    """Tests for ScanResult model."""
    
    def test_create_scan_result(self) -> None:
        """Test creating ScanResult instance."""
        pkg = PackageInfo(name="requests", version="2.31.0")
        result = ScanResult(
            packages=[pkg],
            total_files=10,
            scanned_files=9,
            scan_time=0.5,
        )
        
        assert len(result.packages) == 1
        assert result.total_files == 10
        assert result.scanned_files == 9
        assert result.scan_time == 0.5
        assert result.errors == []
    
    def test_scan_result_defaults(self) -> None:
        """Test ScanResult default values."""
        result = ScanResult(packages=[], total_files=0, scanned_files=0)
        
        assert result.errors == []
        assert result.scan_time == 0.0
    
    def test_success_rate(self) -> None:
        """Test success rate calculation."""
        result = ScanResult(packages=[], total_files=10, scanned_files=8)
        assert result.success_rate == 0.8
        
        result_empty = ScanResult(packages=[], total_files=0, scanned_files=0)
        assert result_empty.success_rate == 0.0
        
        result_perfect = ScanResult(packages=[], total_files=5, scanned_files=5)
        assert result_perfect.success_rate == 1.0
    
    def test_get_external_packages(self) -> None:
        """Test getting external packages."""
        pkg1 = PackageInfo(name="requests")
        pkg2 = PackageInfo(name="flask")
        
        result = ScanResult(
            packages=[pkg1, pkg2],
            total_files=1,
            scanned_files=1,
        )
        
        external = result.get_external_packages()
        assert len(external) == 2
        assert pkg1 in external
        assert pkg2 in external
