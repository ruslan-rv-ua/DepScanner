# DepScanner Examples

Real-world examples of using DepScanner.

## Example 1: Generate requirements.txt

Scan your project and create a `requirements.txt` file:

```python
from depscanner import scan_directory

# Scan the current directory
result = scan_directory(".")

# Generate requirements.txt
with open("requirements.txt", "w") as f:
    for pkg in sorted(result.packages, key=lambda p: p.name):
        if pkg.version:
            f.write(f"{pkg.name}=={pkg.version}\n")
        else:
            f.write(f"{pkg.name}\n")

print(f"Generated requirements.txt with {len(result.packages)} packages")
```

## Example 2: Check Dependencies

Compare installed dependencies with what's actually used:

```python
from depscanner import scan_directory
import sys

# Read current requirements
with open("requirements.txt") as f:
    declared = set()
    for line in f:
        if line.strip() and not line.startswith("#"):
            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
            declared.add(pkg_name.lower())

# Scan project
result = scan_directory("src/")
found = {pkg.name.lower() for pkg in result.packages}

# Find differences
undeclared = found - declared
unused = declared - found

if undeclared:
    print("⚠️  Undeclared dependencies:")
    for pkg in sorted(undeclared):
        print(f"  - {pkg}")

if unused:
    print("\n📦 Declared but not used:")
    for pkg in sorted(unused):
        print(f"  - {pkg}")

if not undeclared and not unused:
    print("✅ All dependencies are properly declared!")
```

## Example 3: Dependency Report

Generate a detailed dependency report:

```python
from depscanner import DependencyScanner
from datetime import datetime

scanner = DependencyScanner()
result = scanner.scan(".")

# Generate report
report = f"""
# Dependency Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics
- Total Python files: {result.total_files}
- Successfully scanned: {result.scanned_files}
- Success rate: {result.success_rate:.1%}
- Scan time: {result.scan_time:.2f}s

## Dependencies ({len(result.packages)})
"""

for pkg in sorted(result.packages, key=lambda p: p.name):
    report += f"\n### {pkg.name}\n"
    report += f"- Version: {pkg.version or 'Unknown'}\n"
    report += f"- Source: {pkg.source}\n"
    report += f"- Used as: {', '.join(pkg.imports)}\n"

if result.errors:
    report += f"\n## Errors ({len(result.errors)})\n"
    for error in result.errors:
        report += f"\n- {error.file_path}\n"
        report += f"  - Type: {error.error_type}\n"
        report += f"  - Message: {error.message}\n"

# Save report
with open("dependency-report.md", "w") as f:
    f.write(report)

print("Report saved to dependency-report.md")
```

## Example 4: CI/CD Integration

Check for new dependencies in CI:

```python
#!/usr/bin/env python3
"""
CI script to check for undeclared dependencies.
Exit code 1 if undeclared dependencies found.
"""

from depscanner import scan_directory
import sys

def load_requirements(filename):
    """Load package names from requirements.txt."""
    packages = set()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                packages.add(pkg.lower())
    return packages

def main():
    # Scan project
    result = scan_directory("src/")
    found = {pkg.name.lower() for pkg in result.packages}
    
    # Load declared dependencies
    try:
        declared = load_requirements("requirements.txt")
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return 1
    
    # Check for undeclared dependencies
    undeclared = found - declared
    
    if undeclared:
        print("❌ Found undeclared dependencies:")
        for pkg in sorted(undeclared):
            print(f"   - {pkg}")
        print("\nPlease add them to requirements.txt")
        return 1
    
    print("✅ All dependencies are declared")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Example 5: Analyze Import Usage

Find which files use which packages:

```python
from depscanner import parse_imports
from pathlib import Path
from collections import defaultdict

def analyze_imports(directory):
    """Analyze which files use which packages."""
    # Collect all imports by package
    package_usage = defaultdict(list)
    
    for py_file in Path(directory).rglob("*.py"):
        try:
            imports = parse_imports(py_file)
            for imp in imports:
                if not imp.is_stdlib:
                    package_usage[imp.module_name].append(str(py_file))
        except Exception:
            continue
    
    # Print usage
    print("Package Usage Report\n" + "=" * 50)
    for package in sorted(package_usage.keys()):
        files = package_usage[package]
        print(f"\n{package} (used in {len(files)} files):")
        for file in files[:5]:  # Show first 5 files
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")

analyze_imports("src/")
```

## Example 6: Version Conflict Detection

Check for version conflicts:

```python
from depscanner import get_local_version, scan_directory

result = scan_directory(".")

conflicts = []
for pkg in result.packages:
    if pkg.version and pkg.source == "local":
        local_version = get_local_version(pkg.name)
        if local_version and local_version != pkg.version:
            conflicts.append((pkg.name, pkg.version, local_version))

if conflicts:
    print("⚠️  Version conflicts detected:")
    for name, expected, actual in conflicts:
        print(f"  {name}: expected {expected}, but {actual} is installed")
else:
    print("✅ No version conflicts")
```

## Example 7: Custom Package Mapping

Handle custom or internal packages:

```python
from depscanner import DependencyScanner, PackageResolver

# Define custom mappings
custom_mapping = {
    "mycompany": "mycompany-internal-package",
    "utils": "mycompany-utils",
    "legacy_module": "legacy-package-v2",
}

# Create resolver with custom mapping
resolver = PackageResolver(mapping=custom_mapping)

# Scan with custom resolver
scanner = DependencyScanner(resolver=resolver)
result = scanner.scan("src/")

for pkg in result.packages:
    print(f"{pkg.name}: {pkg.version}")
```

## Example 8: Selective Scanning

Scan only specific parts of a project:

```python
from depscanner import scan_files
from pathlib import Path

# Find only application code (exclude tests, examples, etc.)
app_files = []
for pattern in ["src/**/*.py", "app/**/*.py"]:
    app_files.extend(Path(".").glob(pattern))

# Scan only application files
result = scan_files(app_files)

print(f"Application dependencies: {len(result.packages)}")
for pkg in result.packages:
    print(f"  - {pkg.name}")

# Scan tests separately
test_files = list(Path("tests").glob("**/*.py"))
test_result = scan_files(test_files)

print(f"\nTest-only dependencies: {len(test_result.packages)}")
test_only = set(pkg.name for pkg in test_result.packages) - set(pkg.name for pkg in result.packages)
for pkg_name in sorted(test_only):
    print(f"  - {pkg_name}")
```

## Example 9: Export to JSON

Export scan results to JSON:

```python
from depscanner import scan_directory
import json

result = scan_directory(".")

# Convert to JSON-serializable format
data = {
    "scan_time": result.scan_time,
    "total_files": result.total_files,
    "scanned_files": result.scanned_files,
    "success_rate": result.success_rate,
    "packages": [
        {
            "name": pkg.name,
            "version": pkg.version,
            "source": pkg.source,
            "imports": pkg.imports,
        }
        for pkg in result.packages
    ],
    "errors": [
        {
            "file": err.file_path,
            "type": err.error_type,
            "message": err.message,
        }
        for err in result.errors
    ],
}

# Save to JSON
with open("dependencies.json", "w") as f:
    json.dump(data, f, indent=2)

print("Exported to dependencies.json")
```

## Example 10: Monitor Dependencies Over Time

Track dependency changes:

```python
from depscanner import scan_directory
import json
from datetime import datetime
from pathlib import Path

def save_snapshot():
    """Save a snapshot of current dependencies."""
    result = scan_directory(".")
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "packages": {
            pkg.name: pkg.version
            for pkg in result.packages
        },
    }
    
    # Load history
    history_file = Path("dependency-history.json")
    if history_file.exists():
        with open(history_file) as f:
            history = json.load(f)
    else:
        history = {"snapshots": []}
    
    # Add new snapshot
    history["snapshots"].append(snapshot)
    
    # Save
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Snapshot saved. Total snapshots: {len(history['snapshots'])}")

def compare_snapshots():
    """Compare latest snapshot with previous."""
    with open("dependency-history.json") as f:
        history = json.load(f)
    
    if len(history["snapshots"]) < 2:
        print("Need at least 2 snapshots to compare")
        return
    
    prev = history["snapshots"][-2]["packages"]
    current = history["snapshots"][-1]["packages"]
    
    # Find changes
    added = set(current.keys()) - set(prev.keys())
    removed = set(prev.keys()) - set(current.keys())
    updated = {
        pkg for pkg in current
        if pkg in prev and current[pkg] != prev[pkg]
    }
    
    print("Dependency Changes:")
    if added:
        print(f"\n✅ Added ({len(added)}):")
        for pkg in sorted(added):
            print(f"  + {pkg} {current[pkg]}")
    
    if removed:
        print(f"\n❌ Removed ({len(removed)}):")
        for pkg in sorted(removed):
            print(f"  - {pkg} {prev[pkg]}")
    
    if updated:
        print(f"\n⬆️  Updated ({len(updated)}):")
        for pkg in sorted(updated):
            print(f"  {pkg}: {prev[pkg]} → {current[pkg]}")
    
    if not (added or removed or updated):
        print("  No changes")

# Usage:
# save_snapshot()  # Run regularly (e.g., on commit)
# compare_snapshots()  # Compare with previous
```
