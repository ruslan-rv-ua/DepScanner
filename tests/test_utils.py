"""Tests for utility functions."""

from pathlib import Path

import pytest

from depscanner.utils import find_python_files, is_python_file, normalize_path, read_file_content


class TestIsPythonFile:
    """Tests for is_python_file function."""

    def test_python_file_extensions(self, tmp_path: Path) -> None:
        """Test that Python file extensions are recognized."""
        py_file = tmp_path / "test.py"
        py_file.touch()
        
        pyw_file = tmp_path / "test.pyw"
        pyw_file.touch()
        
        assert is_python_file(py_file) is True
        assert is_python_file(pyw_file) is True

    def test_non_python_files(self, tmp_path: Path) -> None:
        """Test that non-Python files are not recognized."""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        
        js_file = tmp_path / "test.js"
        js_file.touch()
        
        assert is_python_file(txt_file) is False
        assert is_python_file(js_file) is False

    def test_with_string_path(self, tmp_path: Path) -> None:
        """Test with string path instead of Path object."""
        py_file = tmp_path / "test.py"
        py_file.touch()
        
        assert is_python_file(str(py_file)) is True


class TestFindPythonFiles:
    """Tests for find_python_files function."""

    def test_find_in_directory(self, tmp_path: Path) -> None:
        """Test finding Python files in a directory."""
        # Create test files
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "readme.txt").touch()
        
        files = find_python_files(tmp_path)
        
        assert len(files) == 2
        assert all(f.suffix == ".py" for f in files)

    def test_find_in_subdirectories(self, tmp_path: Path) -> None:
        """Test finding Python files in subdirectories."""
        # Create nested structure
        (tmp_path / "file1.py").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.py").touch()
        
        files = find_python_files(tmp_path)
        
        assert len(files) == 2

    def test_ignore_directories(self, tmp_path: Path) -> None:
        """Test ignoring specific directories."""
        # Create structure with venv
        (tmp_path / "main.py").touch()
        venv_dir = tmp_path / "venv"
        venv_dir.mkdir()
        (venv_dir / "lib.py").touch()
        
        files = find_python_files(tmp_path, ignore_dirs=["venv"])
        
        assert len(files) == 1
        assert files[0].name == "main.py"

    def test_nonexistent_directory(self) -> None:
        """Test handling of nonexistent directory."""
        result = find_python_files("/nonexistent/path/to/directory")
        
        assert result == []

    def test_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test handling when path is a file, not directory."""
        file_path = tmp_path / "test.py"
        file_path.touch()
        
        result = find_python_files(file_path)
        
        assert result == []

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Test handling of empty directory."""
        result = find_python_files(tmp_path)
        
        assert result == []


class TestNormalizePath:
    """Tests for normalize_path function."""

    def test_normalize_relative_path(self, tmp_path: Path) -> None:
        """Test normalizing relative path."""
        result = normalize_path(".")
        
        assert isinstance(result, str)
        assert Path(result).is_absolute()

    def test_normalize_absolute_path(self, tmp_path: Path) -> None:
        """Test normalizing absolute path."""
        result = normalize_path(tmp_path)
        
        assert isinstance(result, str)
        assert Path(result).is_absolute()
        assert str(tmp_path.resolve()) == result


class TestReadFileContent:
    """Tests for read_file_content function."""

    def test_read_file(self, tmp_path: Path) -> None:
        """Test reading file content."""
        file_path = tmp_path / "test.py"
        content = "import os\nimport sys\n"
        file_path.write_text(content)
        
        result = read_file_content(file_path)
        
        assert result == content

    def test_read_with_encoding(self, tmp_path: Path) -> None:
        """Test reading file with specific encoding."""
        file_path = tmp_path / "test.py"
        content = "# -*- coding: utf-8 -*-\nimport os\n"
        file_path.write_text(content, encoding="utf-8")
        
        result = read_file_content(file_path, encoding="utf-8")
        
        assert result == content

    def test_read_nonexistent_file(self) -> None:
        """Test reading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            read_file_content("/nonexistent/file.py")

    def test_read_with_encoding_error(self, tmp_path: Path) -> None:
        """Test reading file with wrong encoding raises error."""
        file_path = tmp_path / "test.py"
        # Write invalid UTF-8 bytes
        file_path.write_bytes(b"\xff\xfe invalid utf-8")
        
        with pytest.raises(UnicodeDecodeError):
            read_file_content(file_path, encoding="utf-8")
