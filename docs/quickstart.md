# DepScanner Quick Start Guide

## Installation

Install DepScanner using pip:

```bash
pip install depscanner
```

Or using uv:

```bash
uv add depscanner
```

## Basic Usage

### Scanning a Project

The simplest way to use DepScanner is to scan a directory:

```python
from depscanner import DependencyScanner

# Create a scanner
scanner = DependencyScanner()

# Scan your project
result = scanner.scan("/path/to/your/project")

# Print discovered dependencies
for package in result.packages:
    if package.version:
        print(f"{package.name}=={package.version}")
    else:
        print(f"{package.name}")
```

### Scanning Specific Files

If you only want to scan specific files:

```python
from depscanner import DependencyScanner

scanner = DependencyScanner()
result = scanner.scan_files([
    "src/main.py",
    "src/utils.py",
    "tests/test_app.py"
])

print(f"Found {len(result.packages)} dependencies")
```

### Using Convenience Functions

DepScanner provides convenience functions for quick operations:

```python
from depscanner import scan_directory, scan_files

# Scan a directory
result = scan_directory("/path/to/project")

# Scan specific files
result = scan_files(["main.py", "utils.py"])
```

## Understanding Results

The `ScanResult` object contains all information about the scan:

```python
result = scanner.scan("/path/to/project")

# Basic stats
print(f"Total files: {result.total_files}")
print(f"Successfully scanned: {result.scanned_files}")
print(f"Success rate: {result.success_rate:.1%}")
print(f"Scan time: {result.scan_time:.2f}s")

# Packages
print(f"Found {len(result.packages)} packages:")
for pkg in result.packages:
    print(f"  - {pkg.name} {pkg.version} (source: {pkg.source})")
    print(f"    Used as: {', '.join(pkg.imports)}")

# Errors (if any)
if result.errors:
    print(f"\n{len(result.errors)} errors occurred:")
    for error in result.errors:
        print(f"  {error.file_path}: {error.error_type}")
```

## Configuration Options

### Ignoring Directories

By default, DepScanner ignores common directories like `.git`, `__pycache__`, `.venv`, etc. You can customize this:

```python
scanner = DependencyScanner(
    ignore_dirs=["custom_dir", "temp", "cache"]
)
result = scanner.scan("/path/to/project")
```

### File Encoding

If your files use a specific encoding:

```python
scanner = DependencyScanner(encoding="utf-8")
# or
scanner = DependencyScanner(encoding="latin-1")
```

### Version Detection

Control how versions are detected:

```python
# Prefer locally installed versions (default)
scanner = DependencyScanner(prefer_local_versions=True)

# Prefer PyPI versions
scanner = DependencyScanner(prefer_local_versions=False)

# Set timeout for PyPI requests
scanner = DependencyScanner(version_timeout=5.0)  # 5 seconds
```

### Custom Package Resolution

If you have custom package name mappings:

```python
from depscanner import DependencyScanner, PackageResolver

# Create custom resolver
resolver = PackageResolver(mapping={
    "my_module": "my-package-name",
    "custom": "custom-package"
})

scanner = DependencyScanner(resolver=resolver)
```

## Common Use Cases

### Generate requirements.txt

```python
from depscanner import scan_directory

result = scan_directory("/path/to/project")

with open("requirements.txt", "w") as f:
    for pkg in result.packages:
        if pkg.version:
            f.write(f"{pkg.name}=={pkg.version}\n")
        else:
            f.write(f"{pkg.name}\n")
```

### Check for Undeclared Dependencies

```python
from depscanner import scan_directory

# Read declared dependencies
with open("requirements.txt") as f:
    declared = {line.split("==")[0].strip() for line in f if line.strip()}

# Scan project
result = scan_directory(".")
found = {pkg.name for pkg in result.packages}

# Find undeclared
undeclared = found - declared
if undeclared:
    print("Undeclared dependencies:")
    for pkg in undeclared:
        print(f"  - {pkg}")
```

### Filter by Source

```python
result = scanner.scan("/path/to/project")

# Get only locally installed packages
local_packages = [pkg for pkg in result.packages if pkg.source == "local"]

# Get packages with unknown versions
unknown = [pkg for pkg in result.packages if pkg.version is None]
```

## Working with Individual Components

### Parse Imports from a File

```python
from depscanner import parse_imports

imports = parse_imports("my_file.py")
for imp in imports:
    print(f"Line {imp.line_number}: import {imp.module_name}")
    print(f"  Is stdlib: {imp.is_stdlib}")
    if not imp.is_stdlib:
        print(f"  Package: {imp.package_name}")
```

### Check if Module is Stdlib

```python
from depscanner import is_stdlib

print(is_stdlib("os"))          # True
print(is_stdlib("requests"))    # False
print(is_stdlib("os.path"))     # True (checks top-level)
```

### Resolve Package Names

```python
from depscanner import resolve_package_name

# Most packages: import name == package name
print(resolve_package_name("requests"))  # "requests"

# Special cases are handled
print(resolve_package_name("cv2"))       # "opencv-python"
print(resolve_package_name("PIL"))       # "Pillow"
print(resolve_package_name("sklearn"))   # "scikit-learn"
```

### Get Package Versions

```python
from depscanner import get_local_version, get_package_version

# Get local version
version = get_local_version("requests")
print(f"Installed: {version}")

# Get version with fallback to PyPI
version, source = get_package_version("requests", prefer_local=True)
print(f"Version: {version} (from {source})")
```

## Error Handling

DepScanner handles errors gracefully:

```python
result = scanner.scan("/path/to/project")

# Check for errors
if result.errors:
    print("Some files couldn't be parsed:")
    for error in result.errors:
        print(f"  {error.file_path}")
        print(f"    Type: {error.error_type}")
        print(f"    Message: {error.message}")
        if error.line_number:
            print(f"    Line: {error.line_number}")

# Success rate
print(f"Success rate: {result.success_rate:.1%}")
```

## Next Steps

- Read the [API Reference](api-reference.md) for complete documentation
- Check [Examples](examples.md) for more usage patterns
- See [Contributing](contributing.md) to contribute to the project
