# API Reference

Complete API documentation for DepScanner.

## Main Classes

### DependencyScanner

Main class for scanning Python projects.

```python
class DependencyScanner:
    def __init__(
        self,
        ignore_dirs: list[str] | None = None,
        follow_symlinks: bool = False,
        encoding: str = "utf-8",
        resolver: PackageResolver | None = None,
        prefer_local_versions: bool = True,
        version_timeout: float = 10.0,
    )
```

**Parameters:**
- `ignore_dirs`: Directory names to ignore during scanning. Default includes common directories like `.git`, `__pycache__`, `.venv`, etc.
- `follow_symlinks`: Whether to follow symbolic links when scanning directories.
- `encoding`: File encoding to use when reading Python files.
- `resolver`: Custom `PackageResolver` instance for package name resolution.
- `prefer_local_versions`: If True, prefer locally installed package versions over PyPI.
- `version_timeout`: Timeout in seconds for PyPI API requests.

**Methods:**

#### scan()

```python
def scan(self, path: str | Path) -> ScanResult
```

Scan a directory (or single file) for Python dependencies.

**Parameters:**
- `path`: Path to directory or file to scan.

**Returns:** `ScanResult` object with discovered dependencies.

#### scan_files()

```python
def scan_files(self, files: list[str | Path]) -> ScanResult
```

Scan specific Python files for dependencies.

**Parameters:**
- `files`: List of file paths to scan.

**Returns:** `ScanResult` object with discovered dependencies.

---

### PackageResolver

Resolves import names to PyPI package names.

```python
class PackageResolver:
    def __init__(self, mapping: dict[str, str] | None = None)
```

**Parameters:**
- `mapping`: Optional custom mapping from import names to package names.

**Methods:**

#### resolve()

```python
def resolve(self, import_name: str) -> str
```

Resolve an import name to a PyPI package name.

**Parameters:**
- `import_name`: Module name as it appears in imports.

**Returns:** PyPI package name.

**Resolution order:**
1. Custom mapping (if provided)
2. `importlib.metadata` lookup
3. Built-in mapping for common edge cases
4. Fallback to import name itself

#### Built-in Mappings

The resolver includes mappings for common packages:
- `cv2` → `opencv-python`
- `PIL` → `Pillow`
- `sklearn` → `scikit-learn`
- `yaml` → `PyYAML`
- `dateutil` → `python-dateutil`
- And more...

---

## Data Models

### ScanResult

Result of scanning a project.

```python
@dataclass
class ScanResult:
    packages: list[PackageInfo]
    total_files: int
    scanned_files: int
    errors: list[ScanError] = field(default_factory=list)
    scan_time: float = 0.0
```

**Attributes:**
- `packages`: List of discovered packages.
- `total_files`: Total number of Python files found.
- `scanned_files`: Number of files successfully scanned.
- `errors`: List of errors encountered during scanning.
- `scan_time`: Time taken to scan in seconds.

**Properties:**

```python
@property
def success_rate(self) -> float
```

Calculate the success rate (scanned_files / total_files).

**Methods:**

```python
def get_external_packages(self) -> list[PackageInfo]
```

Get only non-stdlib packages (same as `packages` as stdlib is already filtered).

---

### PackageInfo

Information about a discovered package.

```python
@dataclass
class PackageInfo:
    name: str
    version: str | None = None
    source: Literal["local", "pypi", "unknown"] = "unknown"
    imports: list[str] = field(default_factory=list)
```

**Attributes:**
- `name`: Package name (as used in requirements).
- `version`: Version string, or None if not determined.
- `source`: Where the version info came from.
- `imports`: List of module names that map to this package.

**Special Methods:**
- Packages are compared by name only (case-insensitive).
- Can be used in sets for deduplication.

---

### ImportInfo

Information about a single import statement.

```python
@dataclass(frozen=True)
class ImportInfo:
    module_name: str
    package_name: str | None
    is_stdlib: bool
    file_path: str
    line_number: int
```

**Attributes:**
- `module_name`: Module name as it appears in the import.
- `package_name`: Corresponding PyPI package name (None for stdlib).
- `is_stdlib`: Whether this is a standard library module.
- `file_path`: Path to file containing the import.
- `line_number`: Line number of the import statement.

---

### ScanError

Information about an error during scanning.

```python
@dataclass
class ScanError:
    file_path: str
    error_type: str
    message: str
    line_number: int | None = None
```

**Attributes:**
- `file_path`: Path to file where error occurred.
- `error_type`: Type of error (e.g., "SyntaxError").
- `message`: Error message.
- `line_number`: Line number if applicable.

---

## Functions

### Scanning Functions

#### scan_directory()

```python
def scan_directory(
    path: str | Path,
    ignore_dirs: list[str] | None = None,
    follow_symlinks: bool = False,
) -> ScanResult
```

Convenience function to scan a directory.

#### scan_files()

```python
def scan_files(files: list[str | Path]) -> ScanResult
```

Convenience function to scan specific files.

---

### Parsing Functions

#### parse_imports()

```python
def parse_imports(
    file_path: str | Path,
    encoding: str = "utf-8"
) -> list[ImportInfo]
```

Parse a Python file and extract all import statements.

**Raises:**
- `InvalidPythonFileError`: If file is not a Python file.
- `FileParsingError`: If file cannot be parsed.

---

### Stdlib Functions

#### is_stdlib()

```python
def is_stdlib(
    module_name: str,
    python_version: tuple[int, int] = (3, 10)
) -> bool
```

Check if a module is part of the standard library.

**Parameters:**
- `module_name`: Module name to check (can be dotted like 'os.path').
- `python_version`: Python version tuple (kept for API compatibility).

**Returns:** True if module is part of stdlib.

**Note:** Uses `sys.stdlib_module_names` from the running Python interpreter.

#### get_stdlib_modules()

```python
def get_stdlib_modules(
    python_version: tuple[int, int] = (3, 10)
) -> set[str]
```

Get the set of standard library module names.

---

### Resolution Functions

#### resolve_package_name()

```python
def resolve_package_name(
    import_name: str,
    resolver: PackageResolver | None = None
) -> str
```

Resolve a single package name.

**Parameters:**
- `import_name`: Module name to resolve.
- `resolver`: Optional PackageResolver instance.

**Returns:** PyPI package name.

---

### Version Functions

#### get_local_version()

```python
def get_local_version(package_name: str) -> str | None
```

Get version of a locally installed package.

**Returns:** Version string or None if not installed.

#### get_package_version()

```python
def get_package_version(
    package_name: str,
    prefer_local: bool = True,
    timeout: float = 10.0,
) -> tuple[str | None, VersionSource]
```

Get package version, trying local then PyPI.

**Returns:** Tuple of (version string or None, source).

**VersionSource:** `Literal["local", "pypi", "unknown"]`

#### get_package_versions()

```python
def get_package_versions(
    packages: list[str],
    prefer_local: bool = True,
    timeout: float = 10.0,
) -> dict[str, tuple[str | None, VersionSource]]
```

Get versions for multiple packages.

**Returns:** Dictionary mapping package names to (version, source) tuples.

---

## Exceptions

### DepScannerError

Base exception for all DepScanner errors.

```python
class DepScannerError(Exception)
```

### FileParsingError

Error parsing a Python file.

```python
class FileParsingError(DepScannerError):
    file_path: str
    original_error: Exception
```

### InvalidPythonFileError

File is not a valid Python file.

```python
class InvalidPythonFileError(DepScannerError):
    file_path: str
```

### PackageResolutionError

Error resolving a package name.

```python
class PackageResolutionError(DepScannerError):
    module_name: str
    reason: str
```

### VersionDetectionError

Error detecting package version.

```python
class VersionDetectionError(DepScannerError):
    package_name: str
    reason: str
```

### PyPIError

Error communicating with PyPI.

```python
class PyPIError(DepScannerError):
    package_name: str
    status_code: int | None
```

---

## Type Aliases

```python
PythonVersion = tuple[int, int]
VersionSource = Literal["local", "pypi", "unknown"]
```

---

## Constants

```python
__version__ = "0.1.0"
```

Current version of DepScanner.
