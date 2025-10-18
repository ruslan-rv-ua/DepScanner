"""Tests for AST parser."""

from pathlib import Path

import pytest

from depscanner.exceptions import FileParsingError, InvalidPythonFileError
from depscanner.parser import (
    extract_imports_from_ast,
    parse_imports,
    parse_multiple_files,
)


class TestParseImports:
    """Tests for parse_imports function."""

    def test_parse_simple_imports(self, sample_project_dir: Path) -> None:
        """Test parsing a file with various import types."""
        file_path = sample_project_dir / "main.py"
        imports = parse_imports(file_path)

        # Should have multiple imports
        assert len(imports) > 0

        # Check for specific imports
        module_names = {imp.module_name for imp in imports}

        # Standard library
        assert "os" in module_names
        assert "sys" in module_names
        assert "pathlib" in module_names

        # Third-party
        assert "requests" in module_names
        assert "numpy" in module_names
        assert "flask" in module_names

    def test_parse_stdlib_detection(self, sample_project_dir: Path) -> None:
        """Test that stdlib modules are correctly identified."""
        file_path = sample_project_dir / "main.py"
        imports = parse_imports(file_path)

        # Find os import
        os_import = next((imp for imp in imports if imp.module_name == "os"), None)
        assert os_import is not None
        assert os_import.is_stdlib is True
        assert os_import.package_name is None  # stdlib modules don't get package names

        # Find requests import
        requests_import = next((imp for imp in imports if imp.module_name == "requests"), None)
        assert requests_import is not None
        assert requests_import.is_stdlib is False
        assert requests_import.package_name == "requests"

    def test_parse_line_numbers(self, sample_project_dir: Path) -> None:
        """Test that line numbers are captured."""
        file_path = sample_project_dir / "main.py"
        imports = parse_imports(file_path)

        # All imports should have line numbers > 0
        assert all(imp.line_number > 0 for imp in imports)

    def test_parse_file_path(self, sample_project_dir: Path) -> None:
        """Test that file paths are captured."""
        file_path = sample_project_dir / "main.py"
        imports = parse_imports(file_path)

        # All imports should have the correct file path
        assert all(imp.file_path == str(file_path) for imp in imports)

    def test_parse_utils_file(self, sample_project_dir: Path) -> None:
        """Test parsing utils.py."""
        file_path = sample_project_dir / "utils.py"
        imports = parse_imports(file_path)

        module_names = {imp.module_name for imp in imports}
        assert "hashlib" in module_names
        assert "datetime" in module_names
        assert "typing" in module_names

    def test_parse_models_file(self, sample_project_dir: Path) -> None:
        """Test parsing models.py."""
        file_path = sample_project_dir / "models.py"
        imports = parse_imports(file_path)

        module_names = {imp.module_name for imp in imports}
        assert "dataclasses" in module_names
        assert "sqlite3" in module_names

    def test_invalid_file_extension(self, tmp_path: Path) -> None:
        """Test error when file is not a Python file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("import os")

        with pytest.raises(InvalidPythonFileError) as exc_info:
            parse_imports(file_path)

        assert str(file_path) in str(exc_info.value)

    def test_syntax_error_file(self, sample_project_dir: Path) -> None:
        """Test handling of syntax errors."""
        file_path = sample_project_dir / "broken.py"

        with pytest.raises(FileParsingError) as exc_info:
            parse_imports(file_path)

        assert str(file_path) in str(exc_info.value)

    def test_nonexistent_file(self) -> None:
        """Test error when file doesn't exist."""
        file_path = Path("/nonexistent/file.py")

        with pytest.raises(FileParsingError):
            parse_imports(file_path)

    def test_encoding_parameter(self, tmp_path: Path) -> None:
        """Test custom encoding parameter."""
        file_path = tmp_path / "test.py"
        file_path.write_text("import os\n", encoding="utf-8")

        imports = parse_imports(file_path, encoding="utf-8")
        assert len(imports) == 1
        assert imports[0].module_name == "os"


class TestExtractImportsFromAst:
    """Tests for extract_imports_from_ast function."""

    def test_extract_from_simple_ast(self) -> None:
        """Test extracting imports from a simple AST."""
        import ast

        code = """
import os
import sys
from pathlib import Path
"""
        tree = ast.parse(code)
        imports = extract_imports_from_ast(tree, "test.py")

        assert len(imports) == 3
        module_names = {imp.module_name for imp in imports}
        assert module_names == {"os", "sys", "pathlib"}

    def test_extract_import_aliases(self) -> None:
        """Test that import aliases are handled."""
        import ast

        code = """
import numpy as np
from pandas import DataFrame as DF
"""
        tree = ast.parse(code)
        imports = extract_imports_from_ast(tree, "test.py")

        # Should extract module names, not aliases
        module_names = {imp.module_name for imp in imports}
        assert "numpy" in module_names
        assert "pandas" in module_names

    def test_extract_multiple_imports_one_line(self) -> None:
        """Test multiple imports on one line."""
        import ast

        code = "import json, re, sys"
        tree = ast.parse(code)
        imports = extract_imports_from_ast(tree, "test.py")

        assert len(imports) == 3
        module_names = {imp.module_name for imp in imports}
        assert module_names == {"json", "re", "sys"}

    def test_extract_from_import_multiple_names(self) -> None:
        """Test from import with multiple names."""
        import ast

        code = "from os import path, environ, getcwd"
        tree = ast.parse(code)
        imports = extract_imports_from_ast(tree, "test.py")

        # Should only extract the module (os), not the individual names
        assert len(imports) == 1
        assert imports[0].module_name == "os"


class TestParseMultipleFiles:
    """Tests for parse_multiple_files function."""

    def test_parse_multiple_valid_files(self, sample_project_dir: Path) -> None:
        """Test parsing multiple valid files."""
        files = [
            sample_project_dir / "main.py",
            sample_project_dir / "utils.py",
            sample_project_dir / "models.py",
        ]

        imports, errors = parse_multiple_files(files)

        # Should have imports from all files
        assert len(imports) > 0

        # Should have no errors
        assert len(errors) == 0

        # Check that we have imports from each file
        file_paths = {imp.file_path for imp in imports}
        assert all(str(f) in file_paths for f in files)

    def test_parse_with_errors_ignore(self, sample_project_dir: Path) -> None:
        """Test parsing files with errors (ignore_errors=True)."""
        files = [
            sample_project_dir / "main.py",
            sample_project_dir / "broken.py",
            sample_project_dir / "utils.py",
        ]

        imports, errors = parse_multiple_files(files, ignore_errors=True)

        # Should have imports from valid files
        assert len(imports) > 0

        # Should have one error (broken.py)
        assert len(errors) == 1
        assert "broken.py" in errors[0][0]

    def test_parse_with_errors_raise(self, sample_project_dir: Path) -> None:
        """Test parsing files with errors (ignore_errors=False)."""
        files = [
            sample_project_dir / "main.py",
            sample_project_dir / "broken.py",
        ]

        with pytest.raises(FileParsingError):
            parse_multiple_files(files, ignore_errors=False)

    def test_parse_empty_list(self) -> None:
        """Test parsing empty file list."""
        imports, errors = parse_multiple_files([])

        assert len(imports) == 0
        assert len(errors) == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test parsing an empty Python file."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")

        imports = parse_imports(file_path)
        assert len(imports) == 0

    def test_file_with_only_comments(self, tmp_path: Path) -> None:
        """Test parsing a file with only comments."""
        file_path = tmp_path / "comments.py"
        file_path.write_text("# This is a comment\n# Another comment\n")

        imports = parse_imports(file_path)
        assert len(imports) == 0

    def test_dotted_module_names(self, tmp_path: Path) -> None:
        """Test parsing dotted module names."""
        file_path = tmp_path / "dotted.py"
        file_path.write_text("import xml.etree.ElementTree\nfrom os.path import join\n")

        imports = parse_imports(file_path)
        module_names = {imp.module_name for imp in imports}

        assert "xml.etree.ElementTree" in module_names
        assert "os.path" in module_names
