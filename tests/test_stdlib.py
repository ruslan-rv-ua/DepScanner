"""Tests for stdlib detection."""

import sys

from depscanner.stdlib import generate_stdlib_list, get_stdlib_modules, is_stdlib


class TestGetStdlibModules:
    """Tests for get_stdlib_modules function."""

    def test_returns_set(self) -> None:
        """Test that function returns a set."""
        result = get_stdlib_modules()
        assert isinstance(result, set)

    def test_contains_common_modules(self) -> None:
        """Test that result contains common stdlib modules."""
        result = get_stdlib_modules()

        # Check for some well-known stdlib modules
        expected_modules = {"os", "sys", "json", "re", "datetime", "pathlib"}
        assert expected_modules.issubset(result)

    def test_uses_sys_stdlib_module_names(self) -> None:
        """Test that function uses sys.stdlib_module_names if available."""
        if hasattr(sys, "stdlib_module_names"):
            result = get_stdlib_modules()
            assert result == set(sys.stdlib_module_names)

    def test_different_python_versions(self) -> None:
        """Test with different Python version parameters."""
        # Note: The python_version parameter doesn't actually change behavior
        # in our implementation (always uses current Python's stdlib)
        result_310 = get_stdlib_modules((3, 10))
        result_311 = get_stdlib_modules((3, 11))
        result_312 = get_stdlib_modules((3, 12))

        # All should return the same (current Python's stdlib)
        assert result_310 == result_311 == result_312


class TestIsStdlib:
    """Tests for is_stdlib function."""

    def test_stdlib_modules(self) -> None:
        """Test that common stdlib modules are detected."""
        stdlib_modules = [
            "os",
            "sys",
            "json",
            "re",
            "datetime",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
        ]

        for module in stdlib_modules:
            assert is_stdlib(module) is True, f"Expected {module} to be stdlib"

    def test_non_stdlib_modules(self) -> None:
        """Test that non-stdlib modules are not detected as stdlib."""
        non_stdlib_modules = [
            "requests",
            "flask",
            "django",
            "numpy",
            "pandas",
            "pytest",
        ]

        for module in non_stdlib_modules:
            assert is_stdlib(module) is False, f"Expected {module} to not be stdlib"

    def test_dotted_imports(self) -> None:
        """Test that dotted imports are handled correctly."""
        # os.path should be detected as stdlib (top-level is 'os')
        assert is_stdlib("os.path") is True
        assert is_stdlib("json.decoder") is True
        assert is_stdlib("collections.abc") is True

        # Non-stdlib dotted imports
        assert is_stdlib("requests.exceptions") is False
        assert is_stdlib("flask.app") is False

    def test_empty_string(self) -> None:
        """Test handling of empty string."""
        # Empty string after split would give ['']
        assert is_stdlib("") is False

    def test_case_sensitivity(self) -> None:
        """Test that module names are case-sensitive."""
        # stdlib modules are lowercase
        assert is_stdlib("os") is True
        assert is_stdlib("OS") is False  # Not in stdlib (case matters)


class TestGenerateStdlibList:
    """Tests for generate_stdlib_list function."""

    def test_returns_same_as_get_stdlib_modules(self) -> None:
        """Test that this is an alias for get_stdlib_modules."""
        result1 = generate_stdlib_list()
        result2 = get_stdlib_modules()

        assert result1 == result2

    def test_with_version_parameter(self) -> None:
        """Test with version parameter."""
        result = generate_stdlib_list((3, 11))
        assert isinstance(result, set)
        assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_stdlib_size(self) -> None:
        """Test that stdlib contains a reasonable number of modules."""
        result = get_stdlib_modules()
        # Python 3.10+ stdlib should have 200+ modules
        assert len(result) > 200

    def test_no_duplicates(self) -> None:
        """Test that there are no duplicate entries."""
        result = get_stdlib_modules()
        result_list = list(result)
        assert len(result) == len(result_list)

    def test_all_strings(self) -> None:
        """Test that all entries are strings."""
        result = get_stdlib_modules()
        assert all(isinstance(item, str) for item in result)

    def test_no_empty_strings(self) -> None:
        """Test that there are no empty strings."""
        result = get_stdlib_modules()
        assert "" not in result
        assert all(len(item) > 0 for item in result)


class TestFallbackFunction:
    """Tests for _get_fallback_stdlib_modules function."""

    def test_fallback_returns_set(self) -> None:
        """Test that fallback function returns a set."""
        from depscanner.stdlib import _get_fallback_stdlib_modules

        result = _get_fallback_stdlib_modules()
        assert isinstance(result, set)

    def test_fallback_contains_common_modules(self) -> None:
        """Test that fallback contains common stdlib modules."""
        from depscanner.stdlib import _get_fallback_stdlib_modules

        result = _get_fallback_stdlib_modules()
        
        # Should contain some basic modules
        assert "os" in result
        assert "sys" in result
        assert "json" in result
        assert "re" in result

    def test_fallback_used_when_no_stdlib_module_names(self) -> None:
        """Test that fallback is used when sys.stdlib_module_names doesn't exist."""
        import unittest.mock as mock

        # Directly test by mocking hasattr to return False
        original_hasattr = hasattr
        
        def mock_hasattr(obj, name):
            if name == "stdlib_module_names":
                return False
            return original_hasattr(obj, name)
        
        with mock.patch("builtins.hasattr", side_effect=mock_hasattr):
            result = get_stdlib_modules()
            
            # Should have used fallback
            assert isinstance(result, set)
            assert "os" in result  # Fallback contains this
