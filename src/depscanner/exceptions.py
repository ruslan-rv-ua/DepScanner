"""Custom exceptions for depscanner."""


class DepScannerError(Exception):
    """Base exception for all depscanner errors."""

    pass


class FileParsingError(DepScannerError):
    """Error parsing a Python file."""

    def __init__(self, file_path: str, original_error: Exception):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Failed to parse {file_path}: {original_error}")


class InvalidPythonFileError(DepScannerError):
    """File is not a valid Python file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Not a valid Python file: {file_path}")


class PackageResolutionError(DepScannerError):
    """Error resolving a package name."""

    def __init__(self, module_name: str, reason: str):
        self.module_name = module_name
        self.reason = reason
        super().__init__(f"Failed to resolve package for module '{module_name}': {reason}")


class VersionDetectionError(DepScannerError):
    """Error detecting package version."""

    def __init__(self, package_name: str, reason: str):
        self.package_name = package_name
        self.reason = reason
        super().__init__(f"Failed to detect version for '{package_name}': {reason}")


class PyPIError(DepScannerError):
    """Error communicating with PyPI."""

    def __init__(self, package_name: str, status_code: int | None = None):
        self.package_name = package_name
        self.status_code = status_code
        msg = f"PyPI error for package '{package_name}'"
        if status_code:
            msg += f" (HTTP {status_code})"
        super().__init__(msg)
