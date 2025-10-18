"""Package version detection utilities."""

import importlib.metadata
from typing import Literal

import httpx
from packaging.version import parse as parse_version

from depscanner.exceptions import PyPIError, VersionDetectionError

VersionSource = Literal["local", "pypi", "unknown"]


def get_local_version(package_name: str) -> str | None:
    """Get the version of a locally installed package.
    
    Args:
        package_name: Name of the package.
    
    Returns:
        Version string if package is installed, None otherwise.
    
    Examples:
        >>> get_local_version("pytest")
        '8.0.0'
        >>> get_local_version("nonexistent-package")
        None
    """
    try:
        version = importlib.metadata.version(package_name)
        return version
    except importlib.metadata.PackageNotFoundError:
        return None
    except Exception:
        return None


def get_pypi_version(package_name: str, timeout: float = 10.0) -> str | None:
    """Get the latest version of a package from PyPI.
    
    Args:
        package_name: Name of the package on PyPI.
        timeout: Request timeout in seconds.
    
    Returns:
        Latest version string if found, None otherwise.
    
    Raises:
        PyPIError: If there's an error communicating with PyPI.
    
    Examples:
        >>> get_pypi_version("requests")
        '2.31.0'
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        
        if response.status_code == 404:
            # Package not found
            return None
        
        if response.status_code != 200:
            raise PyPIError(package_name, response.status_code)
        
        data = response.json()
        version = data.get("info", {}).get("version")
        
        return version
    
    except httpx.TimeoutException:
        # Timeout - return None instead of raising
        return None
    except httpx.HTTPError as e:
        # Network error - return None
        return None
    except PyPIError:
        # Re-raise PyPIError
        raise
    except Exception as e:
        # Unexpected error
        return None


def get_package_version(
    package_name: str,
    prefer_local: bool = True,
    timeout: float = 10.0,
) -> tuple[str | None, VersionSource]:
    """Get the version of a package, trying local then PyPI.
    
    Args:
        package_name: Name of the package.
        prefer_local: If True, try local first, then PyPI. If False, try PyPI first.
        timeout: Timeout for PyPI requests in seconds.
    
    Returns:
        Tuple of (version string or None, source of version).
    
    Examples:
        >>> get_package_version("pytest")
        ('8.0.0', 'local')
    """
    if prefer_local:
        # Try local first
        local_version = get_local_version(package_name)
        if local_version:
            return (local_version, "local")
        
        # Try PyPI as fallback
        pypi_version = get_pypi_version(package_name, timeout=timeout)
        if pypi_version:
            return (pypi_version, "pypi")
    else:
        # Try PyPI first
        pypi_version = get_pypi_version(package_name, timeout=timeout)
        if pypi_version:
            return (pypi_version, "pypi")
        
        # Try local as fallback
        local_version = get_local_version(package_name)
        if local_version:
            return (local_version, "local")
    
    return (None, "unknown")


def get_package_versions(
    packages: list[str],
    prefer_local: bool = True,
    timeout: float = 10.0,
) -> dict[str, tuple[str | None, VersionSource]]:
    """Get versions for multiple packages.
    
    Args:
        packages: List of package names.
        prefer_local: If True, try local first, then PyPI.
        timeout: Timeout for PyPI requests in seconds.
    
    Returns:
        Dictionary mapping package names to (version, source) tuples.
    
    Examples:
        >>> get_package_versions(["pytest", "requests"])
        {'pytest': ('8.0.0', 'local'), 'requests': ('2.31.0', 'local')}
    """
    results: dict[str, tuple[str | None, VersionSource]] = {}
    
    for package in packages:
        version, source = get_package_version(package, prefer_local=prefer_local, timeout=timeout)
        results[package] = (version, source)
    
    return results


def compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings.
    
    Args:
        version1: First version string.
        version2: Second version string.
    
    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2.
    
    Examples:
        >>> compare_versions("1.0.0", "2.0.0")
        -1
        >>> compare_versions("2.0.0", "1.0.0")
        1
        >>> compare_versions("1.0.0", "1.0.0")
        0
    """
    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except Exception:
        # If parsing fails, do string comparison
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0
