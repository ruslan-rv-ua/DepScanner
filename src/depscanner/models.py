"""Data models for depscanner."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ImportInfo:
    """Information about a single import statement.
    
    Attributes:
        module_name: The name of the module as it appears in the import
        package_name: The PyPI package name (may differ from module_name)
        is_stdlib: Whether this is a standard library module
        file_path: Path to the file where the import was found
        line_number: Line number where the import was found
    """
    
    module_name: str
    package_name: str | None
    is_stdlib: bool
    file_path: str
    line_number: int


@dataclass
class PackageInfo:
    """Information about a discovered package dependency.
    
    Attributes:
        name: Package name (as it would appear in requirements)
        version: Version string (None if not determined)
        source: Where the version info came from ('local' or 'pypi')
        imports: List of module names that map to this package
    """
    
    name: str
    version: str | None = None
    source: Literal["local", "pypi", "unknown"] = "unknown"
    imports: list[str] = field(default_factory=list)
    
    def __eq__(self, other: object) -> bool:
        """Compare packages by name only."""
        if not isinstance(other, PackageInfo):
            return NotImplemented
        return self.name.lower() == other.name.lower()
    
    def __hash__(self) -> int:
        """Hash by lowercase name for use in sets."""
        return hash(self.name.lower())


@dataclass
class ScanError:
    """Information about an error during scanning.
    
    Attributes:
        file_path: Path to the file where the error occurred
        error_type: Type of error
        message: Error message
        line_number: Line number if applicable
    """
    
    file_path: str
    error_type: str
    message: str
    line_number: int | None = None


@dataclass
class ScanResult:
    """Result of scanning a project for dependencies.
    
    Attributes:
        packages: List of discovered packages
        total_files: Total number of Python files found
        scanned_files: Number of files successfully scanned
        errors: List of errors encountered during scanning
        scan_time: Time taken to scan in seconds
    """
    
    packages: list[PackageInfo]
    total_files: int
    scanned_files: int
    errors: list[ScanError] = field(default_factory=list)
    scan_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of scanning."""
        if self.total_files == 0:
            return 0.0
        return self.scanned_files / self.total_files
    
    def get_external_packages(self) -> list[PackageInfo]:
        """Get only non-stdlib packages."""
        # Note: packages in ScanResult are already filtered to non-stdlib
        return self.packages
