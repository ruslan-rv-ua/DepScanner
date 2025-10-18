# DepScanner Documentation

Welcome to the DepScanner documentation!

## Getting Started

- **[Quick Start Guide](quickstart.md)** - Get up and running quickly
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples](examples.md)** - Real-world usage examples
- **[Contributing](contributing.md)** - How to contribute to the project

## What is DepScanner?

DepScanner is a modern Python dependency scanner designed for programmatic use. It analyzes Python projects to discover their dependencies using AST-based parsing.

## Key Features

- 🔍 **AST-based parsing** - Accurate import detection using Python's AST
- 📦 **Smart package resolution** - Automatic mapping from imports to PyPI packages
- 🎯 **Stdlib detection** - Built-in standard library filtering (Python 3.10+)
- 🔢 **Version detection** - Both local and PyPI version lookup
- 🚀 **Pure Python** - No external binaries required
- 📊 **Programmatic API** - Use as a library, not a CLI tool

## Quick Example

```python
from depscanner import DependencyScanner

scanner = DependencyScanner()
result = scanner.scan("/path/to/project")

for package in result.packages:
    print(f"{package.name}=={package.version}")
```

## Architecture

DepScanner consists of several components:

1. **Scanner** - Main orchestrator that coordinates all components
2. **Parser** - AST-based Python file parser for extracting imports
3. **Resolver** - Maps import names to PyPI package names
4. **Version Detector** - Determines package versions (local or PyPI)
5. **Stdlib Detector** - Identifies standard library modules

## Use Cases

- Generate `requirements.txt` files
- Verify all dependencies are declared
- Analyze dependency usage across projects
- CI/CD dependency checking
- Dependency auditing and reporting

## Requirements

- Python 3.10 or higher
- Dependencies:
  - `httpx` - For PyPI API requests
  - `packaging` - For version string handling

## Installation

```bash
pip install depscanner
```

Or with uv:

```bash
uv add depscanner
```

## Documentation Contents

### [Quick Start Guide](quickstart.md)

Learn the basics:
- Installation
- Basic usage
- Configuration options
- Common use cases
- Working with components
- Error handling

### [API Reference](api-reference.md)

Complete API documentation:
- `DependencyScanner` class
- `PackageResolver` class
- Data models (`ScanResult`, `PackageInfo`, etc.)
- All functions and methods
- Exceptions
- Type definitions

### [Examples](examples.md)

Real-world examples:
1. Generate requirements.txt
2. Check dependencies
3. Dependency reports
4. CI/CD integration
5. Import usage analysis
6. Version conflict detection
7. Custom package mapping
8. Selective scanning
9. Export to JSON
10. Monitor dependencies over time

### [Contributing](contributing.md)

Development guide:
- Development setup
- Project structure
- Development workflow
- Code style guidelines
- Testing guidelines
- Adding new features
- Documentation updates

## Support

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Ask questions or share ideas
- **Documentation**: This documentation and inline docstrings

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0 (Current)

- Initial release
- AST-based import parsing
- Package name resolution with built-in mappings
- Version detection (local and PyPI)
- Standard library detection using `sys.stdlib_module_names`
- Comprehensive test suite (90%+ coverage)
- Full API documentation

## Roadmap

Future enhancements may include:
- Parallel file processing for better performance
- Caching for PyPI requests
- Support for conda environments
- Dependency graph visualization
- Integration with popular tools

---

**Happy scanning!** 🔍
