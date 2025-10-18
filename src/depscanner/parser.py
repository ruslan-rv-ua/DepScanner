"""AST-based Python file parser for extracting imports."""

import ast
from pathlib import Path

from depscanner.exceptions import FileParsingError, InvalidPythonFileError
from depscanner.models import ImportInfo
from depscanner.stdlib import is_stdlib
from depscanner.utils import is_python_file, read_file_content


def parse_imports(file_path: str | Path, encoding: str = "utf-8") -> list[ImportInfo]:
    """Parse a Python file and extract all import statements.

    Args:
        file_path: Path to the Python file.
        encoding: File encoding (default: utf-8).

    Returns:
        List of ImportInfo objects for all imports found.

    Raises:
        InvalidPythonFileError: If the file is not a Python file.
        FileParsingError: If the file cannot be parsed.
    """
    path = Path(file_path)

    # Check if it's a Python file
    if not is_python_file(path):
        raise InvalidPythonFileError(str(path))

    try:
        # Read file content
        content = read_file_content(path, encoding=encoding)

        # Parse AST
        tree = ast.parse(content, filename=str(path))

        # Extract imports
        imports = extract_imports_from_ast(tree, str(path))

        return imports

    except SyntaxError as e:
        raise FileParsingError(str(path), e)
    except UnicodeDecodeError as e:
        raise FileParsingError(str(path), e)
    except Exception as e:
        raise FileParsingError(str(path), e)


def extract_imports_from_ast(tree: ast.AST, file_path: str) -> list[ImportInfo]:
    """Extract import information from an AST tree.

    Args:
        tree: AST tree of the Python file.
        file_path: Path to the file (for metadata).

    Returns:
        List of ImportInfo objects.
    """
    imports: list[ImportInfo] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Handle: import module, import module as alias
            for alias in node.names:
                module_name = alias.name
                import_info = _create_import_info(module_name, file_path, node.lineno)
                imports.append(import_info)

        elif isinstance(node, ast.ImportFrom):
            # Handle: from module import name, from module import *
            if node.module is not None:
                module_name = node.module
                import_info = _create_import_info(module_name, file_path, node.lineno)
                imports.append(import_info)

    return imports


def _create_import_info(module_name: str, file_path: str, line_number: int) -> ImportInfo:
    """Create an ImportInfo object.

    Args:
        module_name: Name of the imported module.
        file_path: Path to the file containing the import.
        line_number: Line number of the import statement.

    Returns:
        ImportInfo object.
    """
    # Check if it's a stdlib module
    is_std = is_stdlib(module_name)

    # For now, package_name is the same as module_name
    # This will be resolved later by the resolver
    package_name = module_name if not is_std else None

    return ImportInfo(
        module_name=module_name,
        package_name=package_name,
        is_stdlib=is_std,
        file_path=file_path,
        line_number=line_number,
    )


def parse_multiple_files(
    file_paths: list[str | Path],
    encoding: str = "utf-8",
    ignore_errors: bool = True,
) -> tuple[list[ImportInfo], list[tuple[str, Exception]]]:
    """Parse multiple Python files and extract imports.

    Args:
        file_paths: List of file paths to parse.
        encoding: File encoding (default: utf-8).
        ignore_errors: If True, continue on errors and return them separately.

    Returns:
        Tuple of (list of ImportInfo objects, list of (file_path, error) tuples).
    """
    all_imports: list[ImportInfo] = []
    errors: list[tuple[str, Exception]] = []

    for file_path in file_paths:
        try:
            imports = parse_imports(file_path, encoding=encoding)
            all_imports.extend(imports)
        except Exception as e:
            if ignore_errors:
                errors.append((str(file_path), e))
            else:
                raise

    return all_imports, errors
