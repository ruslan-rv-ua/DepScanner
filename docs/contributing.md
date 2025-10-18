# Contributing to DepScanner

Thank you for your interest in contributing to DepScanner! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/ruslan-rv-ua/depscanner.git
cd depscanner

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest
```

## Project Structure

```
depscanner/
├── src/depscanner/      # Source code
│   ├── __init__.py      # Public API
│   ├── scanner.py       # Main scanner
│   ├── parser.py        # AST parser
│   ├── resolver.py      # Package resolution
│   ├── version.py       # Version detection
│   ├── stdlib.py        # Stdlib detection
│   ├── models.py        # Data models
│   ├── exceptions.py    # Exceptions
│   └── utils.py         # Utilities
├── tests/               # Test files
│   ├── test_*.py        # Unit tests
│   └── fixtures/        # Test fixtures
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Follow these guidelines:
- Write clear, concise code
- Add type hints to all functions
- Include docstrings (Google style)
- Follow PEP 8 style guide

### 3. Write Tests

- Add tests for new features
- Maintain > 90% code coverage
- Test edge cases

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/depscanner --cov-report=html

# Run specific test file
uv run pytest tests/test_scanner.py -v
```

### 4. Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Type checking
uv run mypy src/
```

### 5. Commit Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add feature: brief description"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues when applicable

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style

We follow PEP 8 with these specifics:
- Line length: 100 characters
- Use double quotes for strings
- Use type hints for all functions
- Google-style docstrings

Example:

```python
def scan_directory(
    path: str | Path,
    ignore_dirs: list[str] | None = None,
) -> ScanResult:
    """Scan a directory for Python dependencies.
    
    Args:
        path: Path to the directory to scan.
        ignore_dirs: Optional list of directory names to ignore.
    
    Returns:
        ScanResult object with discovered dependencies.
    
    Examples:
        >>> result = scan_directory("/path/to/project")
        >>> len(result.packages)
        10
    """
    ...
```

### Type Hints

Always use type hints:

```python
# Good
def process_file(file_path: str | Path) -> list[ImportInfo]:
    ...

# Bad
def process_file(file_path):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(arg1: str, arg2: int = 0) -> bool:
    """Brief description of function.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2. Defaults to 0.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: Description of when this is raised.
    
    Examples:
        >>> example_function("test")
        True
    """
    ...
```

## Testing Guidelines

### Test Structure

```python
class TestClassName:
    """Tests for ClassName."""
    
    def test_basic_functionality(self) -> None:
        """Test basic functionality."""
        # Arrange
        scanner = DependencyScanner()
        
        # Act
        result = scanner.scan("/path")
        
        # Assert
        assert result is not None
```

### Test Coverage

- Aim for > 90% coverage
- Test happy paths
- Test error conditions
- Test edge cases

```python
def test_edge_case_empty_file(self, tmp_path: Path) -> None:
    """Test handling of empty files."""
    file_path = tmp_path / "empty.py"
    file_path.write_text("")
    
    result = parse_imports(file_path)
    assert len(result) == 0
```

### Mocking

Use pytest-mock for external dependencies:

```python
def test_pypi_request(self, mocker: MockerFixture) -> None:
    """Test PyPI request handling."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"info": {"version": "1.0.0"}}
    
    mocker.patch("httpx.get", return_value=mock_response)
    
    version = get_pypi_version("requests")
    assert version == "1.0.0"
```

## Adding New Features

### 1. Parser Enhancements

If adding new import detection:

```python
# In parser.py
def extract_imports_from_ast(tree: ast.AST, file_path: str) -> list[ImportInfo]:
    imports: list[ImportInfo] = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Handle regular imports
            ...
        elif isinstance(node, ast.ImportFrom):
            # Handle from imports
            ...
        # Add your new case here
        elif isinstance(node, YourNewNodeType):
            ...
    
    return imports
```

### 2. Resolver Enhancements

If adding new package mappings:

```python
# In resolver.py
def _get_builtin_mapping(self) -> dict[str, str]:
    return {
        # Existing mappings
        "cv2": "opencv-python",
        # Add new mappings
        "new_module": "new-package",
    }
```

### 3. Version Detection

If adding new version sources:

```python
# In version.py
def get_package_version(...) -> tuple[str | None, VersionSource]:
    # Try local
    if prefer_local:
        ...
    
    # Try PyPI
    ...
    
    # Add your new source
    ...
```

## Documentation

### Updating Documentation

When adding features, update:

1. **Docstrings** in code
2. **API Reference** (`docs/api-reference.md`)
3. **Quick Start** (`docs/quickstart.md`) if relevant
4. **Examples** (`docs/examples.md`) for new use cases
5. **README.md** for major features

### Documentation Style

- Be clear and concise
- Include code examples
- Show expected output
- Explain edge cases

## Release Process

(For maintainers)

1. Update version in `src/depscanner/__init__.py`
2. Update version in `pyproject.toml`
3. Update CHANGELOG (if exists)
4. Create git tag: `git tag v0.x.0`
5. Push tag: `git push origin v0.x.0`
6. Build: `uv build`
7. Publish: `uv publish`

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues/discussions first

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Collaborate openly

Thank you for contributing to DepScanner! 🎉
