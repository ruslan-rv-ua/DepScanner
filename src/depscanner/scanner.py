"""Main dependency scanner implementation."""

import time
from pathlib import Path

from depscanner.models import PackageInfo, ScanError, ScanResult
from depscanner.parser import parse_multiple_files
from depscanner.resolver import PackageResolver
from depscanner.utils import find_python_files, is_python_file
from depscanner.version import get_package_versions


class DependencyScanner:
    """Main class for scanning Python projects for dependencies."""
    
    def __init__(
        self,
        ignore_dirs: list[str] | None = None,
        follow_symlinks: bool = False,
        encoding: str = "utf-8",
        resolver: PackageResolver | None = None,
        prefer_local_versions: bool = True,
        version_timeout: float = 10.0,
    ):
        """Initialize the dependency scanner.
        
        Args:
            ignore_dirs: List of directory names to ignore during scanning.
            follow_symlinks: Whether to follow symbolic links.
            encoding: File encoding to use when reading Python files.
            resolver: Optional custom PackageResolver instance.
            prefer_local_versions: If True, prefer locally installed versions.
            version_timeout: Timeout for PyPI version requests in seconds.
        """
        self.ignore_dirs = ignore_dirs or [
            ".git",
            ".hg",
            ".svn",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            ".venv",
            "venv",
            "env",
            "ENV",
            "node_modules",
            ".eggs",
            "*.egg-info",
            "build",
            "dist",
        ]
        self.follow_symlinks = follow_symlinks
        self.encoding = encoding
        self.resolver = resolver or PackageResolver()
        self.prefer_local_versions = prefer_local_versions
        self.version_timeout = version_timeout
    
    def scan(self, path: str | Path) -> ScanResult:
        """Scan a directory for Python dependencies.
        
        Args:
            path: Path to the directory to scan.
        
        Returns:
            ScanResult object containing discovered packages and metadata.
        
        Examples:
            >>> scanner = DependencyScanner()
            >>> result = scanner.scan("/path/to/project")
            >>> for pkg in result.packages:
            ...     print(f"{pkg.name}=={pkg.version}")
        """
        start_time = time.time()
        path_obj = Path(path)
        
        # Find all Python files
        if path_obj.is_file() and is_python_file(path_obj):
            python_files = [path_obj]
        else:
            python_files = find_python_files(
                path_obj,
                ignore_dirs=self.ignore_dirs,
                follow_symlinks=self.follow_symlinks,
            )
        
        total_files = len(python_files)
        
        # Parse all files to extract imports
        imports, parse_errors = parse_multiple_files(
            python_files,
            encoding=self.encoding,
            ignore_errors=True,
        )
        
        scanned_files = total_files - len(parse_errors)
        
        # Convert parse errors to ScanError objects
        errors = [
            ScanError(
                file_path=file_path,
                error_type=type(error).__name__,
                message=str(error),
            )
            for file_path, error in parse_errors
        ]
        
        # Filter out stdlib imports and collect unique external packages
        external_imports = [imp for imp in imports if not imp.is_stdlib]
        
        # Group imports by package name
        package_imports: dict[str, list[str]] = {}
        for imp in external_imports:
            # Resolve import name to package name
            resolved_name = self.resolver.resolve(imp.module_name)
            
            # For dotted names, try to get the top-level package
            # e.g., "django.http" -> "django"
            package_name = resolved_name.split(".")[0]
            
            if package_name not in package_imports:
                package_imports[package_name] = []
            
            if imp.module_name not in package_imports[package_name]:
                package_imports[package_name].append(imp.module_name)
        
        # Get versions for all packages
        package_names = list(package_imports.keys())
        versions_dict = get_package_versions(
            package_names,
            prefer_local=self.prefer_local_versions,
            timeout=self.version_timeout,
        )
        
        # Create PackageInfo objects
        packages = []
        for package_name in sorted(package_names):
            version, source = versions_dict[package_name]
            
            pkg_info = PackageInfo(
                name=package_name,
                version=version,
                source=source,
                imports=package_imports[package_name],
            )
            packages.append(pkg_info)
        
        # Calculate scan time
        scan_time = time.time() - start_time
        
        return ScanResult(
            packages=packages,
            total_files=total_files,
            scanned_files=scanned_files,
            errors=errors,
            scan_time=scan_time,
        )
    
    def scan_files(self, files: list[str | Path]) -> ScanResult:
        """Scan specific Python files for dependencies.
        
        Args:
            files: List of file paths to scan.
        
        Returns:
            ScanResult object containing discovered packages and metadata.
        
        Examples:
            >>> scanner = DependencyScanner()
            >>> result = scanner.scan_files(["main.py", "utils.py"])
        """
        start_time = time.time()
        
        # Convert to Path objects and filter Python files
        python_files = [Path(f) for f in files if is_python_file(f)]
        
        total_files = len(python_files)
        
        # Parse all files
        imports, parse_errors = parse_multiple_files(
            python_files,
            encoding=self.encoding,
            ignore_errors=True,
        )
        
        scanned_files = total_files - len(parse_errors)
        
        # Convert parse errors to ScanError objects
        errors = [
            ScanError(
                file_path=file_path,
                error_type=type(error).__name__,
                message=str(error),
            )
            for file_path, error in parse_errors
        ]
        
        # Filter out stdlib imports
        external_imports = [imp for imp in imports if not imp.is_stdlib]
        
        # Group by package name
        package_imports: dict[str, list[str]] = {}
        for imp in external_imports:
            resolved_name = self.resolver.resolve(imp.module_name)
            
            # For dotted names, get the top-level package
            package_name = resolved_name.split(".")[0]
            
            if package_name not in package_imports:
                package_imports[package_name] = []
            
            if imp.module_name not in package_imports[package_name]:
                package_imports[package_name].append(imp.module_name)
        
        # Get versions
        package_names = list(package_imports.keys())
        versions_dict = get_package_versions(
            package_names,
            prefer_local=self.prefer_local_versions,
            timeout=self.version_timeout,
        )
        
        # Create PackageInfo objects
        packages = []
        for package_name in sorted(package_names):
            version, source = versions_dict[package_name]
            
            pkg_info = PackageInfo(
                name=package_name,
                version=version,
                source=source,
                imports=package_imports[package_name],
            )
            packages.append(pkg_info)
        
        scan_time = time.time() - start_time
        
        return ScanResult(
            packages=packages,
            total_files=total_files,
            scanned_files=scanned_files,
            errors=errors,
            scan_time=scan_time,
        )


# Convenience functions

def scan_directory(
    path: str | Path,
    ignore_dirs: list[str] | None = None,
    follow_symlinks: bool = False,
) -> ScanResult:
    """Convenience function to scan a directory.
    
    Args:
        path: Path to directory to scan.
        ignore_dirs: Directory names to ignore.
        follow_symlinks: Whether to follow symlinks.
    
    Returns:
        ScanResult object.
    """
    scanner = DependencyScanner(
        ignore_dirs=ignore_dirs,
        follow_symlinks=follow_symlinks,
    )
    return scanner.scan(path)


def scan_files(files: list[str | Path]) -> ScanResult:
    """Convenience function to scan specific files.
    
    Args:
        files: List of file paths.
    
    Returns:
        ScanResult object.
    """
    scanner = DependencyScanner()
    return scanner.scan_files(files)
