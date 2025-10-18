"""DepScanner - Modern Python dependency scanner.

A programmatic library for detecting and analyzing dependencies in Python projects.
"""

from depscanner.exceptions import (
    DepScannerError,
    FileParsingError,
    InvalidPythonFileError,
    PackageResolutionError,
    PyPIError,
    VersionDetectionError,
)
from depscanner.models import ImportInfo, PackageInfo, ScanError, ScanResult
from depscanner.parser import parse_imports
from depscanner.resolver import PackageResolver, resolve_package_name
from depscanner.scanner import DependencyScanner, scan_directory, scan_files
from depscanner.stdlib import is_stdlib
from depscanner.version import get_local_version, get_package_version

__version__ = "0.1.0"

__all__ = [
    # Main scanner
    "DependencyScanner",
    "scan_directory",
    "scan_files",
    # Models
    "ImportInfo",
    "PackageInfo",
    "ScanError",
    "ScanResult",
    # Parser
    "parse_imports",
    # Resolver
    "PackageResolver",
    "resolve_package_name",
    # Stdlib
    "is_stdlib",
    # Version
    "get_local_version",
    "get_package_version",
    # Exceptions
    "DepScannerError",
    "FileParsingError",
    "InvalidPythonFileError",
    "PackageResolutionError",
    "VersionDetectionError",
    "PyPIError",
    # Version
    "__version__",
]
