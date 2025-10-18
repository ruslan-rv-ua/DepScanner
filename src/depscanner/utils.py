"""Utility functions for depscanner."""

import os
from pathlib import Path


def is_python_file(file_path: str | Path) -> bool:
    """Check if a file is a Python file.

    Args:
        file_path: Path to the file to check.

    Returns:
        True if the file has .py or .pyw extension.
    """
    path = Path(file_path)
    return path.suffix in (".py", ".pyw")


def find_python_files(
    directory: str | Path,
    ignore_dirs: list[str] | None = None,
    follow_symlinks: bool = False,
) -> list[Path]:
    """Find all Python files in a directory recursively.

    Args:
        directory: Directory to search.
        ignore_dirs: List of directory names to ignore.
        follow_symlinks: Whether to follow symbolic links.

    Returns:
        List of paths to Python files.
    """
    if ignore_dirs is None:
        ignore_dirs = []

    ignore_dirs_set = set(ignore_dirs)
    python_files: list[Path] = []
    directory_path = Path(directory)

    if not directory_path.exists():
        return []

    if not directory_path.is_dir():
        return []

    for root, dirs, files in os.walk(directory_path, followlinks=follow_symlinks):
        root_path = Path(root)

        # Remove ignored directories from the search
        dirs[:] = [d for d in dirs if d not in ignore_dirs_set]

        # Check each file
        for file in files:
            file_path = root_path / file
            if is_python_file(file_path):
                python_files.append(file_path)

    return python_files


def normalize_path(path: str | Path) -> str:
    """Normalize a file path to absolute path.

    Args:
        path: Path to normalize.

    Returns:
        Absolute path as string.
    """
    return str(Path(path).resolve())


def read_file_content(file_path: str | Path, encoding: str = "utf-8") -> str:
    """Read file content with error handling.

    Args:
        file_path: Path to the file.
        encoding: File encoding.

    Returns:
        File content as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        UnicodeDecodeError: If file cannot be decoded.
    """
    path = Path(file_path)
    return path.read_text(encoding=encoding)
