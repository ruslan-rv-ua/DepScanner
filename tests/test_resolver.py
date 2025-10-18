"""Tests for package resolver."""


from depscanner.resolver import PackageResolver, resolve_package_name


class TestPackageResolver:
    """Tests for PackageResolver class."""

    def test_init_without_mapping(self) -> None:
        """Test initialization without custom mapping."""
        resolver = PackageResolver()
        assert resolver._custom_mapping == {}
        assert resolver._cache == {}

    def test_init_with_custom_mapping(self) -> None:
        """Test initialization with custom mapping."""
        custom_mapping = {"mymodule": "my-package"}
        resolver = PackageResolver(mapping=custom_mapping)
        assert resolver._custom_mapping == custom_mapping

    def test_resolve_simple_package(self) -> None:
        """Test resolving a simple package name."""
        resolver = PackageResolver()

        # Most packages: import name == package name
        assert resolver.resolve("pytest") == "pytest"
        assert resolver.resolve("requests") == "requests"

    def test_resolve_with_custom_mapping(self) -> None:
        """Test resolving with custom mapping."""
        custom_mapping = {"mymodule": "my-package"}
        resolver = PackageResolver(mapping=custom_mapping)

        assert resolver.resolve("mymodule") == "my-package"

    def test_resolve_builtin_mappings(self) -> None:
        """Test resolving packages with known edge cases."""
        resolver = PackageResolver()

        # Test common edge cases
        assert resolver.resolve("cv2") == "opencv-python"
        assert resolver.resolve("PIL") == "Pillow"
        assert resolver.resolve("sklearn") == "scikit-learn"
        assert resolver.resolve("yaml") == "PyYAML"
        assert resolver.resolve("dateutil") == "python-dateutil"

    def test_resolve_dotted_imports(self) -> None:
        """Test resolving dotted import names."""
        resolver = PackageResolver()

        # Should extract top-level module
        result = resolver.resolve("cv2.cv2")
        assert result == "opencv-python"

    def test_cache_functionality(self) -> None:
        """Test that resolution results are cached."""
        resolver = PackageResolver()

        # First resolution
        result1 = resolver.resolve("pytest")

        # Should be in cache now
        assert "pytest" in resolver._cache

        # Second resolution should use cache
        result2 = resolver.resolve("pytest")
        assert result1 == result2

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        resolver = PackageResolver()

        resolver.resolve("pytest")
        assert len(resolver._cache) > 0

        resolver.clear_cache()
        assert len(resolver._cache) == 0

    def test_custom_mapping_priority(self) -> None:
        """Test that custom mapping takes priority over builtin."""
        custom_mapping = {"cv2": "my-custom-opencv"}
        resolver = PackageResolver(mapping=custom_mapping)

        # Should use custom mapping, not builtin
        assert resolver.resolve("cv2") == "my-custom-opencv"

    def test_load_mapping(self) -> None:
        """Test loading the complete mapping."""
        custom_mapping = {"mymodule": "my-package"}
        resolver = PackageResolver(mapping=custom_mapping)

        mapping = resolver.load_mapping()

        # Should contain both custom and builtin
        assert "mymodule" in mapping
        assert "cv2" in mapping
        assert mapping["mymodule"] == "my-package"
        assert mapping["cv2"] == "opencv-python"

    def test_fallback_to_import_name(self) -> None:
        """Test that unknown packages fallback to import name."""
        resolver = PackageResolver()

        # For unknown packages, should return the import name itself
        unknown_package = "some_unknown_package_xyz"
        assert resolver.resolve(unknown_package) == unknown_package


class TestResolvePackageName:
    """Tests for resolve_package_name convenience function."""

    def test_without_resolver(self) -> None:
        """Test using convenience function without providing resolver."""
        result = resolve_package_name("requests")
        assert result == "requests"

    def test_with_resolver(self) -> None:
        """Test using convenience function with custom resolver."""
        custom_mapping = {"mymodule": "my-package"}
        resolver = PackageResolver(mapping=custom_mapping)

        result = resolve_package_name("mymodule", resolver=resolver)
        assert result == "my-package"

    def test_builtin_mappings(self) -> None:
        """Test convenience function with builtin mappings."""
        assert resolve_package_name("cv2") == "opencv-python"
        assert resolve_package_name("PIL") == "Pillow"
        assert resolve_package_name("sklearn") == "scikit-learn"


class TestBuiltinMapping:
    """Tests for builtin mapping completeness."""

    def test_common_packages(self) -> None:
        """Test that common problematic packages are in builtin mapping."""
        resolver = PackageResolver()
        builtin = resolver._get_builtin_mapping()

        # Computer vision
        assert "cv2" in builtin
        assert "PIL" in builtin

        # Scientific
        assert "sklearn" in builtin
        assert "skimage" in builtin

        # YAML
        assert "yaml" in builtin

        # Utilities
        assert "dateutil" in builtin
        assert "dotenv" in builtin

    def test_builtin_mapping_values(self) -> None:
        """Test that builtin mapping has correct values."""
        resolver = PackageResolver()
        builtin = resolver._get_builtin_mapping()

        assert builtin["cv2"] == "opencv-python"
        assert builtin["PIL"] == "Pillow"
        assert builtin["sklearn"] == "scikit-learn"
        assert builtin["yaml"] == "PyYAML"


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_string(self) -> None:
        """Test resolving empty string."""
        resolver = PackageResolver()
        result = resolver.resolve("")
        assert result == ""

    def test_special_characters(self) -> None:
        """Test package names with special characters."""
        resolver = PackageResolver()

        # Should handle these gracefully
        result = resolver.resolve("package-name")
        assert isinstance(result, str)

    def test_very_long_name(self) -> None:
        """Test very long package name."""
        resolver = PackageResolver()
        long_name = "a" * 1000

        result = resolver.resolve(long_name)
        assert isinstance(result, str)

    def test_cache_with_multiple_packages(self) -> None:
        """Test cache with multiple different packages."""
        resolver = PackageResolver()

        packages = ["requests", "flask", "django", "numpy", "pandas"]
        for pkg in packages:
            resolver.resolve(pkg)

        # All should be in cache
        for pkg in packages:
            assert pkg in resolver._cache

    def test_resolve_from_metadata_error_handling(self) -> None:
        """Test that _resolve_via_metadata handles errors gracefully."""
        import unittest.mock as mock

        resolver = PackageResolver()

        # Test that method returns None when exception occurs
        with mock.patch("importlib.metadata.distributions", side_effect=Exception("test error")):
            result = resolver._resolve_via_metadata("test_package")
            assert result is None

    def test_resolve_from_metadata_with_missing_top_level(self) -> None:
        """Test _resolve_via_metadata when top_level.txt is missing."""
        import unittest.mock as mock

        resolver = PackageResolver()

        # Create a mock distribution that raises FileNotFoundError
        mock_dist = mock.MagicMock()
        mock_dist.read_text.side_effect = FileNotFoundError("top_level.txt not found")

        with mock.patch("importlib.metadata.distributions", return_value=[mock_dist]):
            result = resolver._resolve_via_metadata("test_package")
            # Should return None as it continues and finds no match
            assert result is None

    def test_resolve_from_metadata_with_missing_name_key(self) -> None:
        """Test _resolve_via_metadata when metadata lacks Name key."""
        import unittest.mock as mock

        resolver = PackageResolver()

        # Create a mock distribution with top_level but missing Name in metadata
        mock_dist = mock.MagicMock()
        mock_dist.read_text.return_value = "test_package"
        mock_dist.metadata = {}  # No "Name" key

        with mock.patch("importlib.metadata.distributions", return_value=[mock_dist]):
            result = resolver._resolve_via_metadata("test_package")
            # Should return None as KeyError is caught
            assert result is None
