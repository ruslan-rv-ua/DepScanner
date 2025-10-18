# План реалізації проєкту DepScanner

**Дата створення:** 18 жовтня 2025  
**Виконавець:** AI Coding Agent  
**Мета:** Створити сучасний Python модуль для визначення залежностей з файлів з початковим кодом

> ⚠️ **ВАЖЛИВО для AI агента:**
> - Цей план призначений для автоматичного виконання
> - Всі рішення вже прийняті - не потрібні додаткові питання
> - Кожна фаза має конкретні deliverables
> - Код генерується згідно специфікацій без відхилень

---

## 1. Огляд проєкту

### 1.1 Назва та призначення
- **Назва:** `depscanner`
- **Призначення:** Програмна бібліотека для сканування Python проєктів та визначення залежностей
- **Відмінності від pipreqs:**
  - Тільки програмне використання (без CLI)
  - Без генерації `requirements.txt`
  - Сучасний підхід до розробки
  - Краща архітектура та тестування

### 1.2 Технічні вимоги
- **Python:** >= 3.10
- **Менеджер пакетів:** uv
- **Тестування:** pytest
- **Документація:** Markdown
- **Підтримка файлів:** `.py`, `.pyw`

---

## 2. Архітектура модуля

### 2.1 Структура проєкту
```
depscanner/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .python-version
│
├── docs/
│   ├── README.md
│   ├── quickstart.md
│   ├── api-reference.md
│   ├── examples.md
│   └── contributing.md
│
├── src/
│   └── depscanner/
│       ├── __init__.py
│       ├── __version__.py
│       ├── scanner.py          # Основний клас DependencyScanner
│       ├── parser.py           # Парсинг AST для виявлення імпортів
│       ├── resolver.py         # Резолвінг імпортів до PyPI пакетів
│       ├── version.py          # Визначення версій пакетів
│       ├── stdlib.py           # Робота зі стандартною бібліотекою
│       ├── models.py           # Dataclass моделі для результатів
│       ├── exceptions.py       # Кастомні винятки
│       └── utils.py            # Допоміжні функції
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_scanner.py
│   ├── test_parser.py
│   ├── test_resolver.py
│   ├── test_version.py
│   ├── test_stdlib.py
│   ├── test_models.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample_project/
│       │   ├── main.py
│       │   ├── utils.py
│       │   └── models.py
│       └── expected_results/
│
└── scripts/
    ├── generate_stdlib.py      # Генерація списку stdlib
    └── update_mapping.py       # Оновлення mapping таблиці
```

### 2.2 Основні компоненти

#### 2.2.1 Models (`models.py`)
```python
@dataclass
class ImportInfo:
    """Інформація про один імпорт"""
    module_name: str              # Ім'я модуля (як в коді)
    package_name: str | None      # Ім'я PyPI пакета
    is_stdlib: bool               # Чи є частиною stdlib
    file_path: str                # Файл де знайдено
    line_number: int              # Номер рядка

@dataclass
class PackageInfo:
    """Інформація про пакет"""
    name: str                     # Назва пакета
    version: str | None           # Версія (якщо знайдена)
    source: str                   # 'local' | 'pypi'
    imports: list[str]            # Список імпортів що вказують на цей пакет

@dataclass
class ScanResult:
    """Результат сканування"""
    packages: list[PackageInfo]   # Знайдені пакети
    total_files: int              # Всього файлів
    scanned_files: int            # Успішно проскановано
    errors: list[dict]            # Помилки під час сканування
    scan_time: float              # Час сканування
```

#### 2.2.2 Scanner (`scanner.py`)
```python
class DependencyScanner:
    """Основний клас для сканування залежностей"""
    
    def __init__(
        self,
        ignore_dirs: list[str] | None = None,
        follow_symlinks: bool = False,
        encoding: str = "utf-8"
    ):
        ...
    
    def scan(self, path: str) -> ScanResult:
        """Сканує директорію та повертає залежності"""
        ...
    
    def scan_files(self, files: list[str]) -> ScanResult:
        """Сканує конкретні файли"""
        ...
```

#### 2.2.3 Parser (`parser.py`)
```python
def parse_imports(file_path: str, encoding: str = "utf-8") -> list[ImportInfo]:
    """Парсить файл та витягує імпорти використовуючи AST"""
    ...

def extract_imports_from_ast(tree: ast.AST, file_path: str) -> list[ImportInfo]:
    """Витягує імпорти з AST дерева"""
    ...
```

#### 2.2.4 Resolver (`resolver.py`)
```python
class PackageResolver:
    """Резолвить імпорти до PyPI пакетів"""
    
    def __init__(self, mapping: dict[str, str] | None = None):
        ...
    
    def resolve(self, import_name: str) -> str:
        """Повертає назву PyPI пакета для імпорту"""
        ...
    
    def load_mapping(self) -> dict[str, str]:
        """Завантажує mapping з різних джерел"""
        ...
```

#### 2.2.5 Version (`version.py`)
```python
def get_local_version(package_name: str) -> str | None:
    """Отримує версію локально встановленого пакета"""
    ...

def get_pypi_version(package_name: str) -> str | None:
    """Отримує останню версію з PyPI"""
    ...

def get_package_versions(
    packages: list[str],
    prefer_local: bool = True
) -> dict[str, str | None]:
    """Отримує версії для списку пакетів"""
    ...
```

#### 2.2.6 Stdlib (`stdlib.py`)
```python
def get_stdlib_modules(python_version: tuple[int, int] = (3, 10)) -> set[str]:
    """Повертає набір модулів стандартної бібліотеки"""
    ...

def is_stdlib(module_name: str, python_version: tuple[int, int] = (3, 10)) -> bool:
    """Перевіряє чи є модуль частиною stdlib"""
    ...

def generate_stdlib_list(python_version: tuple[int, int]) -> set[str]:
    """Генерує список stdlib модулів програмно"""
    ...
```

---

## 3. Покращення відносно pipreqs

### 3.1 Stdlib Detection
**Проблема в pipreqs:** Статичний файл `stdlib` який треба вручну оновлювати

**Рішення в depscanner:**
- Використання `sys.stdlib_module_names` (Python 3.10+)
- Програмна генерація списку для різних версій Python
- Підтримка версіонування stdlib

### 3.2 Import Mapping
**Проблема в pipreqs:** Статичний файл `mapping` (1157 рядків)

**Рішення в depscanner:**
- Використання `importlib.metadata` для автоматичного визначення
- Парсинг `top_level.txt` з встановлених пакетів
- Опціональний кеш для швидкості
- Можливість доповнення власним mapping

### 3.3 AST Parsing
**Покращення:**
- Краще опрацювання різних типів імпортів
- Збереження метаданих (файл, рядок)
- Обробка винятків на рівні окремих файлів

### 3.4 Version Detection
**Покращення:**
- Пріоритетність локальних/PyPI версій (налаштування)
- Кешування запитів до PyPI
- Batch запити для оптимізації
- Timeout і retry механізми

---

## 4. API та використання

### 4.1 Базове використання
```python
from depscanner import DependencyScanner

# Створення сканера
scanner = DependencyScanner()

# Сканування проєкту
result = scanner.scan("/path/to/project")

# Доступ до результатів
for package in result.packages:
    print(f"{package.name}=={package.version}")
```

### 4.2 Розширене використання
```python
from depscanner import DependencyScanner, get_package_versions

# Налаштований сканер
scanner = DependencyScanner(
    ignore_dirs=[".venv", "tests", "__pycache__"],
    follow_symlinks=False,
    encoding="utf-8"
)

# Сканування конкретних файлів
result = scanner.scan_files([
    "src/main.py",
    "src/utils.py"
])

# Фільтрація результатів
external_packages = [
    pkg for pkg in result.packages 
    if not pkg.is_stdlib
]

# Отримання версій
versions = get_package_versions(
    [pkg.name for pkg in external_packages],
    prefer_local=True
)
```

### 4.3 Функціональний API
```python
from depscanner import (
    scan_directory,
    parse_imports,
    resolve_package_name,
    get_local_version,
    is_stdlib_module
)

# Функціональний підхід
imports = parse_imports("main.py")
packages = [resolve_package_name(imp.module_name) for imp in imports]
versions = {pkg: get_local_version(pkg) for pkg in packages}
```

---

## 5. Тестування

### 5.1 Структура тестів
- **Unit tests:** Кожен модуль окремо
- **Integration tests:** Тестування всього flow
- **Fixture tests:** Тестові проєкти з відомими залежностями

### 5.2 Coverage
- **Мета:** >= 90% покриття коду
- **Інструменти:** pytest-cov

### 5.3 Тестові сценарії
1. Парсинг різних типів імпортів
2. Виявлення stdlib модулів
3. Резолвінг до PyPI пакетів
4. Отримання версій (локально та PyPI)
5. Обробка помилок
6. Edge cases (порожні файли, невалідний Python, тощо)

---

## 6. Налаштування проєкту

### 6.1 pyproject.toml
```toml
[project]
name = "depscanner"
version = "0.1.0"
description = "Modern Python dependency scanner"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27.0",      # Для PyPI запитів
    "packaging>=24.0",    # Для роботи з версіями
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --cov=src/depscanner --cov-report=html --cov-report=term"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
```

### 6.2 Використання uv
```bash
# Ініціалізація проєкту
uv init depscanner
cd depscanner

# Встановлення залежностей
uv sync

# Запуск тестів
uv run pytest

# Форматування коду
uv run ruff format .
uv run ruff check --fix .

# Type checking
uv run mypy src/
```

---

## 7. Документація (ТОЧНІ СПЕЦИФІКАЦІЇ)

### 7.1 README.md (Базова версія для Фази 1)
**Файл:** `c:\dev_test\depscanner\README.md`
**Вміст:**
```markdown
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

```bash
pip install depscanner
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

## License

MIT License - see LICENSE file for details.

## Development Status

⚠️ This project is in active development (v0.1.0)
```

### 7.2 docs/quickstart.md (Для Фази 9)
**Створити детальний quickstart з прикладами**

### 7.3 docs/api-reference.md (Для Фази 9)
**Створити повний API reference для всіх публічних класів та функцій**

### 7.4 docs/examples.md (Для Фази 9)
**Створити приклади використання**

### 7.5 docs/contributing.md (Для Фази 9)
**Створити гайд для contributors**

---

## 8. Етапи реалізації (Детальні інструкції для AI агента)

> **Правила виконання:**
> 1. Виконувати фази строго по порядку
> 2. Не переходити до наступної фази без завершення попередньої
> 3. Створювати всі файли згідно специфікацій
> 4. Запускати тести після кожного модуля
> 5. Використовувати точні назви файлів та шляхи як вказано

### Фаза 1: Базова структура проєкту

**Deliverables:**
1. ✅ Створити нову директорію `c:\dev_test\depscanner`
2. ✅ Створити всю структуру директорій згідно розділу 2.1
3. ✅ Ініціалізувати Git репозиторій
4. ✅ Створити файли конфігурації

**Детальні кроки:**

#### Крок 1.1: Створення структури
```cmd
mkdir c:\dev_test\depscanner
cd c:\dev_test\depscanner
mkdir src\depscanner
mkdir tests\fixtures\sample_project
mkdir tests\fixtures\expected_results
mkdir docs
mkdir scripts
```

#### Крок 1.2: Ініціалізація uv
```cmd
uv init --name depscanner --lib
```

#### Крок 1.3: Створення `.gitignore`
**Файл:** `c:\dev_test\depscanner\.gitignore`
**Вміст:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# uv
.uv/
uv.lock
```

#### Крок 1.4: Створення `.python-version`
**Файл:** `c:\dev_test\depscanner\.python-version`
**Вміст:**
```
3.10
```

#### Крок 1.5: Створення `pyproject.toml`
**Файл:** `c:\dev_test\depscanner\pyproject.toml`
**Вміст:**
```toml
[project]
name = "depscanner"
version = "0.1.0"
description = "Modern Python dependency scanner - programmatic library for detecting dependencies in Python projects"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "DepScanner Contributors"}
]
keywords = ["dependencies", "imports", "scanner", "python", "static-analysis"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Quality Assurance",
]

dependencies = [
    "httpx>=0.27.0",
    "packaging>=24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/depscanner"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "-v",
    "--cov=src/depscanner",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
]

[tool.ruff]
line-length = 100
target-version = "py310"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
```

#### Крок 1.6: Створення `LICENSE`
**Файл:** `c:\dev_test\depscanner\LICENSE`
**Вміст:**
```
MIT License

Copyright (c) 2025 DepScanner Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### Крок 1.7: Створення початкового README.md
**Файл:** `c:\dev_test\depscanner\README.md`
**Вміст:** (див. розділ 7.1 - базова версія)

#### Крок 1.8: Ініціалізація Git
```cmd
cd c:\dev_test\depscanner
git init
git add .
git commit -m "Initial project structure"
```

#### Крок 1.9: Встановлення залежностей
```cmd
uv sync --all-extras
```

**Критерії завершення Фази 1:**
- ✅ Всі директорії створені
- ✅ Всі конфігураційні файли на місці
- ✅ Git репозиторій ініціалізовано
- ✅ uv працює та залежності встановлені
- ✅ Можна запустити `uv run pytest` (хоч тестів ще немає)

---

### Фаза 2: Моделі та виключення

**Deliverables:**
1. ✅ `src/depscanner/models.py` з усіма dataclass моделями
2. ✅ `src/depscanner/exceptions.py` з кастомними винятками
3. ✅ `tests/test_models.py` з тестами для моделей

#### Крок 2.1: Створення `models.py`
**Файл:** `src/depscanner/models.py`
**Вміст:**
```python
"""Data models for depscanner."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class ImportInfo:
    """Information about a single import statement.
    
    Attributes:
        module_name: The name of the module as it appears in the import
        package_name: The PyPI package name (may differ from module_name)
        is_stdlib: Whether this is a standard library module
        file_path: Path to the file where the import was found
        line_number: Line number where the import was found
    """
    
    module_name: str
    package_name: str | None
    is_stdlib: bool
    file_path: str
    line_number: int


@dataclass
class PackageInfo:
    """Information about a discovered package dependency.
    
    Attributes:
        name: Package name (as it would appear in requirements)
        version: Version string (None if not determined)
        source: Where the version info came from ('local' or 'pypi')
        imports: List of module names that map to this package
    """
    
    name: str
    version: str | None = None
    source: Literal["local", "pypi", "unknown"] = "unknown"
    imports: list[str] = field(default_factory=list)
    
    def __eq__(self, other: object) -> bool:
        """Compare packages by name only."""
        if not isinstance(other, PackageInfo):
            return NotImplemented
        return self.name.lower() == other.name.lower()
    
    def __hash__(self) -> int:
        """Hash by lowercase name for use in sets."""
        return hash(self.name.lower())


@dataclass
class ScanError:
    """Information about an error during scanning.
    
    Attributes:
        file_path: Path to the file where the error occurred
        error_type: Type of error
        message: Error message
        line_number: Line number if applicable
    """
    
    file_path: str
    error_type: str
    message: str
    line_number: int | None = None


@dataclass
class ScanResult:
    """Result of scanning a project for dependencies.
    
    Attributes:
        packages: List of discovered packages
        total_files: Total number of Python files found
        scanned_files: Number of files successfully scanned
        errors: List of errors encountered during scanning
        scan_time: Time taken to scan in seconds
    """
    
    packages: list[PackageInfo]
    total_files: int
    scanned_files: int
    errors: list[ScanError] = field(default_factory=list)
    scan_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of scanning."""
        if self.total_files == 0:
            return 0.0
        return self.scanned_files / self.total_files
    
    def get_external_packages(self) -> list[PackageInfo]:
        """Get only non-stdlib packages."""
        # Note: packages in ScanResult are already filtered to non-stdlib
        return self.packages
```

#### Крок 2.2: Створення `exceptions.py`
**Файл:** `src/depscanner/exceptions.py`
**Вміст:**
```python
"""Custom exceptions for depscanner."""


class DepScannerError(Exception):
    """Base exception for all depscanner errors."""
    
    pass


class FileParsingError(DepScannerError):
    """Error parsing a Python file."""
    
    def __init__(self, file_path: str, original_error: Exception):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Failed to parse {file_path}: {original_error}")


class InvalidPythonFileError(DepScannerError):
    """File is not a valid Python file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Not a valid Python file: {file_path}")


class PackageResolutionError(DepScannerError):
    """Error resolving a package name."""
    
    def __init__(self, module_name: str, reason: str):
        self.module_name = module_name
        self.reason = reason
        super().__init__(f"Failed to resolve package for module '{module_name}': {reason}")


class VersionDetectionError(DepScannerError):
    """Error detecting package version."""
    
    def __init__(self, package_name: str, reason: str):
        self.package_name = package_name
        self.reason = reason
        super().__init__(f"Failed to detect version for '{package_name}': {reason}")


class PyPIError(DepScannerError):
    """Error communicating with PyPI."""
    
    def __init__(self, package_name: str, status_code: int | None = None):
        self.package_name = package_name
        self.status_code = status_code
        msg = f"PyPI error for package '{package_name}'"
        if status_code:
            msg += f" (HTTP {status_code})"
        super().__init__(msg)
```

#### Крок 2.3: Створення `__init__.py`
**Файл:** `src/depscanner/__init__.py`
**Вміст:**
```python
"""DepScanner - Modern Python dependency scanner.

A programmatic library for detecting and analyzing dependencies in Python projects.
"""

from depscanner.models import ImportInfo, PackageInfo, ScanError, ScanResult
from depscanner.exceptions import (
    DepScannerError,
    FileParsingError,
    InvalidPythonFileError,
    PackageResolutionError,
    VersionDetectionError,
    PyPIError,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "ImportInfo",
    "PackageInfo",
    "ScanError",
    "ScanResult",
    # Exceptions
    "DepScannerError",
    "FileParsingError",
    "InvalidPythonFileError",
    "PackageResolutionError",
    "VersionDetectionError",
    "PyPIError",
    # Version
    "__version__",
]
```

#### Крок 2.4: Створення тестів для моделей
**Файл:** `tests/test_models.py`
**Вміст:**
```python
"""Tests for data models."""

import pytest
from depscanner.models import ImportInfo, PackageInfo, ScanError, ScanResult


class TestImportInfo:
    """Tests for ImportInfo model."""
    
    def test_create_import_info(self):
        """Test creating ImportInfo instance."""
        import_info = ImportInfo(
            module_name="requests",
            package_name="requests",
            is_stdlib=False,
            file_path="/path/to/file.py",
            line_number=1,
        )
        
        assert import_info.module_name == "requests"
        assert import_info.package_name == "requests"
        assert import_info.is_stdlib is False
        assert import_info.file_path == "/path/to/file.py"
        assert import_info.line_number == 1
    
    def test_import_info_is_frozen(self):
        """Test that ImportInfo is immutable."""
        import_info = ImportInfo(
            module_name="test",
            package_name="test",
            is_stdlib=False,
            file_path="test.py",
            line_number=1,
        )
        
        with pytest.raises(AttributeError):
            import_info.module_name = "changed"  # type: ignore


class TestPackageInfo:
    """Tests for PackageInfo model."""
    
    def test_create_package_info(self):
        """Test creating PackageInfo instance."""
        pkg = PackageInfo(
            name="requests",
            version="2.31.0",
            source="local",
            imports=["requests"],
        )
        
        assert pkg.name == "requests"
        assert pkg.version == "2.31.0"
        assert pkg.source == "local"
        assert pkg.imports == ["requests"]
    
    def test_package_info_defaults(self):
        """Test PackageInfo default values."""
        pkg = PackageInfo(name="test")
        
        assert pkg.version is None
        assert pkg.source == "unknown"
        assert pkg.imports == []
    
    def test_package_equality(self):
        """Test that packages are equal if names match (case-insensitive)."""
        pkg1 = PackageInfo(name="Requests", version="1.0")
        pkg2 = PackageInfo(name="requests", version="2.0")
        pkg3 = PackageInfo(name="flask", version="1.0")
        
        assert pkg1 == pkg2
        assert pkg1 != pkg3
    
    def test_package_hash(self):
        """Test that packages can be used in sets."""
        pkg1 = PackageInfo(name="Requests")
        pkg2 = PackageInfo(name="requests")
        pkg3 = PackageInfo(name="Flask")
        
        packages = {pkg1, pkg2, pkg3}
        assert len(packages) == 2  # Requests and Flask


class TestScanError:
    """Tests for ScanError model."""
    
    def test_create_scan_error(self):
        """Test creating ScanError instance."""
        error = ScanError(
            file_path="/path/to/file.py",
            error_type="SyntaxError",
            message="Invalid syntax",
            line_number=10,
        )
        
        assert error.file_path == "/path/to/file.py"
        assert error.error_type == "SyntaxError"
        assert error.message == "Invalid syntax"
        assert error.line_number == 10
    
    def test_scan_error_no_line_number(self):
        """Test ScanError without line number."""
        error = ScanError(
            file_path="test.py",
            error_type="IOError",
            message="File not found",
        )
        
        assert error.line_number is None


class TestScanResult:
    """Tests for ScanResult model."""
    
    def test_create_scan_result(self):
        """Test creating ScanResult instance."""
        pkg = PackageInfo(name="requests", version="2.31.0")
        result = ScanResult(
            packages=[pkg],
            total_files=10,
            scanned_files=9,
            scan_time=0.5,
        )
        
        assert len(result.packages) == 1
        assert result.total_files == 10
        assert result.scanned_files == 9
        assert result.scan_time == 0.5
        assert result.errors == []
    
    def test_scan_result_defaults(self):
        """Test ScanResult default values."""
        result = ScanResult(packages=[], total_files=0, scanned_files=0)
        
        assert result.errors == []
        assert result.scan_time == 0.0
    
    def test_success_rate(self):
        """Test success rate calculation."""
        result = ScanResult(packages=[], total_files=10, scanned_files=8)
        assert result.success_rate == 0.8
        
        result_empty = ScanResult(packages=[], total_files=0, scanned_files=0)
        assert result_empty.success_rate == 0.0
        
        result_perfect = ScanResult(packages=[], total_files=5, scanned_files=5)
        assert result_perfect.success_rate == 1.0
    
    def test_get_external_packages(self):
        """Test getting external packages."""
        pkg1 = PackageInfo(name="requests")
        pkg2 = PackageInfo(name="flask")
        
        result = ScanResult(
            packages=[pkg1, pkg2],
            total_files=1,
            scanned_files=1,
        )
        
        external = result.get_external_packages()
        assert len(external) == 2
        assert pkg1 in external
        assert pkg2 in external
```

#### Крок 2.5: Створення `conftest.py` для pytest
**Файл:** `tests/conftest.py`
**Вміст:**
```python
"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_project_dir(fixtures_dir: Path) -> Path:
    """Return the path to the sample project fixture."""
    return fixtures_dir / "sample_project"


@pytest.fixture
def expected_results_dir(fixtures_dir: Path) -> Path:
    """Return the path to expected results directory."""
    return fixtures_dir / "expected_results"
```

#### Крок 2.6: Створення `tests/__init__.py`
**Файл:** `tests/__init__.py`
**Вміст:**
```python
"""Tests for depscanner."""
```

#### Крок 2.7: Запуск тестів
```cmd
cd c:\dev_test\depscanner
uv run pytest tests/test_models.py -v
```

**Критерії завершення Фази 2:**
- ✅ Всі моделі створені та документовані
- ✅ Всі винятки створені
- ✅ Тести для моделей написані та проходять
- ✅ Coverage для models.py >= 90%

---

### Фаза 3: Stdlib detection

**Deliverables:**
1. ✅ `src/depscanner/stdlib.py` з функціями для роботи зі stdlib
2. ✅ `tests/test_stdlib.py` з тестами
3. ✅ `scripts/generate_stdlib.py` для генерації списків

#### Крок 3.1: Створення `stdlib.py`
**Файл:** `src/depscanner/stdlib.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ - використання sys.stdlib_module_names)

#### Крок 3.2: Створення тестів `test_stdlib.py`
**Файл:** `tests/test_stdlib.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ)

#### Крок 3.3: Створення скрипта `generate_stdlib.py`
**Файл:** `scripts/generate_stdlib.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ)

**Критерії завершення Фази 3:**
- ✅ stdlib.py реалізовано
- ✅ Тести проходять
- ✅ Скрипт генерації працює
- ✅ Coverage >= 90%

---

### Фаза 4: AST Parser

**Deliverables:**
1. ✅ `src/depscanner/parser.py`
2. ✅ `src/depscanner/utils.py`
3. ✅ `tests/test_parser.py`
4. ✅ Тестові fixtures

#### Крок 4.1: Створення `parser.py`
**Файл:** `src/depscanner/parser.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ - AST parsing з підтримкою import/from import)

#### Крок 4.2: Створення `utils.py`
**Файл:** `src/depscanner/utils.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ - допоміжні функції)

#### Крок 4.3: Створення тестових файлів
**Створити тестові Python файли в `tests/fixtures/sample_project/`**

#### Крок 4.4: Створення тестів
**Файл:** `tests/test_parser.py`
**Вміст:** (ПОВНА СПЕЦИФІКАЦІЯ)

**Критерії завершення Фази 4:**
- ✅ Parser реалізовано
- ✅ Підтримка всіх типів імпортів
- ✅ Обробка помилок
- ✅ Тести проходять
- ✅ Coverage >= 90%

---

### Фаза 5: Package Resolver

**Deliverables:**
1. ✅ `src/depscanner/resolver.py`
2. ✅ `tests/test_resolver.py`
3. ✅ `scripts/update_mapping.py`

**Специфікація:** (ДЕТАЛЬНА РЕАЛІЗАЦІЯ через importlib.metadata)

**Критерії завершення Фази 5:**
- ✅ Resolver реалізовано
- ✅ Автоматичний mapping працює
- ✅ Fallback на статичний mapping
- ✅ Тести проходять
- ✅ Coverage >= 90%

---

### Фаза 6: Version Detection

**Deliverables:**
1. ✅ `src/depscanner/version.py`
2. ✅ `tests/test_version.py`

**Специфікація:** (ДЕТАЛЬНА РЕАЛІЗАЦІЯ - local + PyPI)

**Критерії завершення Фази 6:**
- ✅ Version detection реалізовано
- ✅ Підтримка локальних версій
- ✅ Підтримка PyPI API
- ✅ Тести з мокуванням HTTP
- ✅ Coverage >= 90%

---

### Фаза 7: Main Scanner

**Deliverables:**
1. ✅ `src/depscanner/scanner.py`
2. ✅ `tests/test_scanner.py`
3. ✅ Оновлення `src/depscanner/__init__.py`

**Специфікація:** (ДЕТАЛЬНА РЕАЛІЗАЦІЯ - інтеграція всіх компонентів)

**Критерії завершення Фази 7:**
- ✅ Scanner реалізовано
- ✅ Інтеграція всіх модулів
- ✅ Тести проходять
- ✅ Coverage >= 90%

---

### Фаза 8: Integration Testing

**Deliverables:**
1. ✅ `tests/test_integration.py`
2. ✅ Реальні тестові проєкти
3. ✅ E2E тести

**Специфікація:** (ДЕТАЛЬНА РЕАЛІЗАЦІЯ)

**Критерії завершення Фази 8:**
- ✅ Інтеграційні тести створені
- ✅ Всі тести проходять
- ✅ Overall coverage >= 90%
- ✅ Продуктивність перевірена

---

### Фаза 9: Документація

**Deliverables:**
1. ✅ Повний `README.md`
2. ✅ `docs/quickstart.md`
3. ✅ `docs/api-reference.md`
4. ✅ `docs/examples.md`
5. ✅ `docs/contributing.md`

**Критерії завершення Фази 9:**
- ✅ Вся документація написана
- ✅ Приклади перевірені
- ✅ API reference повний

---



## 9. Залежності

### 9.1 Runtime dependencies
- **httpx**: Сучасний HTTP клієнт для PyPI API
- **packaging**: Робота з версіями пакетів

### 9.2 Development dependencies
- **pytest**: Тестування
- **pytest-cov**: Coverage
- **pytest-mock**: Mocking
- **ruff**: Linting та форматування
- **mypy**: Type checking

---

## 10. Рішення по залежностях та інтеграціям

### 10.1 Runtime dependencies (ОСТАТОЧНЕ РІШЕННЯ)
- **httpx==0.27.0** - Сучасний HTTP клієнт для PyPI API (замість requests)
- **packaging==24.0** - Робота з версіями пакетів (стандарт de-facto)

### 10.2 Development dependencies (ОСТАТОЧНЕ РІШЕННЯ)
- **pytest==8.0.0** - Тестування
- **pytest-cov==5.0.0** - Coverage
- **pytest-mock==3.14.0** - Mocking для HTTP та файлової системи
- **ruff==0.6.0** - Linting та форматування (замість flake8 + black)
- **mypy==1.11.0** - Type checking

### 10.3 Інтеграції (РІШЕННЯ)
- **НІ інтеграцій** з GitHub Actions, pre-commit тощо в v0.1
- Тільки чистий Python модуль

---

## 11. Метрики успіху

### 11.1 Технічні метрики
- Test coverage >= 90%
- Type coverage 100%
- Zero critical bugs
- Performance: < 1s для проєкту з 100 файлами

### 11.2 Якісні метрики
- Зрозуміла документація
- Зручний API
- Легке встановлення
- Мінімум залежностей

---

## 12. Обробка ризиків (КОНКРЕТНІ РІШЕННЯ)

### 12.1 PyPI API rate limiting
**РІШЕННЯ:**
- Використовувати httpx з timeout=10s
- НЕ робити кешування в v0.1 (буде в v0.2)
- Fallback: якщо PyPI не відповідає, version=None
- Batch запити: НЕ в v0.1

### 12.2 Складність mapping
**РІШЕННЯ:**
- Пріоритет #1: `importlib.metadata` (автоматично)
- Пріоритет #2: Простий статичний dict для edge cases
- Статичний mapping буде мінімальним (~50 відомих випадків)
- Format: `{"cv2": "opencv-python", "PIL": "Pillow", ...}`

### 12.3 Продуктивність
**РІШЕННЯ для v0.1:**
- Sequential processing (без parallel)
- Timeout 10s для PyPI запитів
- Мета: < 5s для проєкту з 100 файлами (acceptable для v0.1)
- Оптимізація буде в v0.2

### 12.4 Encoding проблеми
**РІШЕННЯ:**
- Default: UTF-8
- Параметр encoding в Scanner.__init__()
- При помилці декодування - додати в errors, продовжити

---

## 13. Інструкції для AI агента

### Загальні правила виконання:

1. **Порядок виконання:**
   - Виконувати фази строго послідовно (1→2→3→...→9)
   - Не пропускати кроки
   - Не переходити до наступної фази без завершення поточної

2. **Створення файлів:**
   - Використовувати ТОЧНІ шляхи як вказано
   - Створювати файли з ПОВНИМ вмістом (не заглушки)
   - Використовувати вказані назви без змін

3. **Код-стайл:**
   - Типізація для всіх функцій (Python 3.10+ type hints)
   - Docstrings в Google style для всіх публічних API
   - Дотримання PEP 8 та налаштувань ruff
   - Використання dataclasses де доречно

4. **Тестування:**
   - Після кожного модуля запускати `uv run pytest`
   - Переконатись що тести проходять перед переходом далі
   - Aim for >= 90% coverage

5. **Коміти:**
   - Після завершення кожної фази робити git commit
   - Формат: `git commit -m "Phase X: [опис фази]"`

6. **Обробка помилок:**
   - Якщо тести не проходять - виправити перед продовженням
   - Якщо щось не зрозуміло - використати логічні значення за замовчуванням з плану

### Як розпочати:

```cmd
# Крок 1: Початок роботи
cd c:\dev_test

# Крок 2: Виконати Фазу 1 повністю
# ... слідувати інструкціям з Фази 1

# Крок 3: Після завершення Фази 1:
cd c:\dev_test\depscanner
git add .
git commit -m "Phase 1: Initial project structure"

# Крок 4: Перейти до Фази 2
# ... і так далі
```

### Контрольний список прогресу:

- [ ] Фаза 1: Базова структура ✅ ГОТОВО: [дата]
- [ ] Фаза 2: Моделі та виключення ✅ ГОТОВО: [дата]
- [ ] Фаза 3: Stdlib detection ✅ ГОТОВО: [дата]  
- [ ] Фаза 4: AST Parser ✅ ГОТОВО: [дата]
- [ ] Фаза 5: Package Resolver ✅ ГОТОВО: [дата]
- [ ] Фаза 6: Version Detection ✅ ГОТОВО: [дата]
- [ ] Фаза 7: Main Scanner ✅ ГОТОВО: [дата]
- [ ] Фаза 8: Integration Testing ✅ ГОТОВО: [дата]
- [ ] Фаза 9: Документація ✅ ГОТОВО: [дата]

### Фінальна перевірка:

```cmd
# Після завершення всіх фаз виконати:
cd c:\dev_test\depscanner

# 1. Всі тести
uv run pytest -v

# 2. Coverage
uv run pytest --cov=src/depscanner --cov-report=term-missing

# 3. Type checking
uv run mypy src/

# 4. Linting
uv run ruff check .

# 5. Formatting
uv run ruff format --check .
```

Якщо всі перевірки проходять - проєкт готовий! ✅

---

## 14. Примітки

- План є ФІНАЛЬНИМ і НЕ змінюється під час виконання
- Всі технічні рішення вже прийняті
- AI агент НЕ має робити припущень - всі специфікації в плані
- Пріоритет: працюючий код з тестами > ідеальний код
- Кожна фаза є atomic - або виконана повністю, або не почата

**Статус:** ✅ READY FOR EXECUTION  
**Версія плану:** 2.0 (AI Agent Optimized)  
**Останнє оновлення:** 18 жовтня 2025

---

## ПОЧАТОК ВИКОНАННЯ

AI Agent, розпочинай з **Фази 1, Крок 1.1** ⬆️

