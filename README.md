# DepScanner

Modern Python dependency scanner - a programmatic library for detecting dependencies in Python projects.

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

## Requirements

- Python 3.10 or higher

## Installation

Currently, DepScanner is only available for installation from GitHub:

```bash
# Using pip
pip install git+https://github.com/ruslan-rv-ua/depscanner.git

# Using uv
uv add git+https://github.com/ruslan-rv-ua/depscanner.git
```

## Acknowledgments

This project was inspired by [pipreqs](https://github.com/bndr/pipreqs), a great tool for generating requirements files. DepScanner expands on the concept by providing a comprehensive programmatic API for dependency scanning and analysis.

## Documentation Contents

### [Quick Start Guide](docs/quickstart.md)

Learn the basics:
- Installation
- Basic usage
- Configuration options
- Common use cases
- Working with components
- Error handling

### [API Reference](docs/api-reference.md)

Complete API documentation:
- `DependencyScanner` class
- `PackageResolver` class
- Data models (`ScanResult`, `PackageInfo`, etc.)
- All functions and methods
- Exceptions
- Type definitions

### [Examples](docs/examples.md)

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

### [Contributing](docs/contributing.md)

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
