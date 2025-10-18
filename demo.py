"""Quick demo of DepScanner on its own codebase."""

from depscanner import DependencyScanner

# Create scanner instance
scanner = DependencyScanner(ignore_dirs={"tests", ".venv", "pipreqs"})

# Scan the depscanner source code
print("🔍 Scanning DepScanner's own codebase...\n")
result = scanner.scan("src/depscanner")

# Display results
print(f"Found {len(result.packages)} dependencies:\n")
for package in sorted(result.packages, key=lambda x: x.name):
    version_str = package.version or "(unknown)"
    print(f"  - {package.name:20} {version_str}")

print(f"\n📊 Statistics:")
print(f"  Success rate: {result.success_rate:.1%}")
print(f"  Scanned files: {result.scanned_files}/{result.total_files}")
print(f"  Scan time: {result.scan_time:.3f}s")

if result.errors:
    print(f"\n⚠️  {len(result.errors)} errors occurred")
