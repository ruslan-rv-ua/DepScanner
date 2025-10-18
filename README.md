# DepScanner

Modern Python dependency scanner - a programmatic library for detecting dependencies in Python projects.

## Features

- 🔍 **AST-based parsing** - Accurate import detection using Python's AST
- 📦 **Smart package resolution** - Automatic mapping from imports to PyPI packages
- 🎯 **Stdlib detection** - Built-in standard library filtering (Python 3.10+)
- 🔢 **Version detection** - Both local and PyPI version lookup
- 🚀 **Pure Python** - No external binaries required
- 📊 **Programmatic API** - Use as a library, not a CLI tool

## Installation

Currently, DepScanner is only available for installation from GitHub:

```bash
# Using pip
pip install git+https://github.com/your-org/depscanner.git

# Using uv
uv add git+https://github.com/your-org/depscanner.git
```

## Quick Start

```python
from depscanner import DependencyScanner

# Create scanner
scanner = DependencyScanner()

# Scan a project
result = scanner.scan("/path/to/project")

# Access results
for package in result.packages:
    print(f"{package.name}=={package.version}")
```

## Requirements

- Python >= 3.10

## Acknowledgments

This project was inspired by [pipreqs](https://github.com/bndr/pipreqs), a great tool for generating requirements files. DepScanner expands on the concept by providing a comprehensive programmatic API for dependency scanning and analysis.

## License

MIT License - see LICENSE file for details.

## Development Status

⚠️ This project is in active development (v0.1.0)
