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

__version__ = "0.1.0"

__all__ = [
    # Models
    "ImportInfo",
    "PackageInfo",
    "ScanError",
    "ScanResult",
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
