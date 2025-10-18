"""Package name resolution utilities."""

import importlib.metadata


class PackageResolver:
    """Resolves import names to PyPI package names."""

    def __init__(self, mapping: dict[str, str] | None = None):
        """Initialize the resolver.

        Args:
            mapping: Optional custom mapping from import names to package names.
                    If None, will use automatic resolution via importlib.metadata.
        """
        self._custom_mapping = mapping or {}
        self._cache: dict[str, str] = {}

    def resolve(self, import_name: str) -> str:
        """Resolve an import name to a PyPI package name.

        Args:
            import_name: The module name as it appears in imports.

        Returns:
            The PyPI package name.

        Examples:
            >>> resolver = PackageResolver()
            >>> resolver.resolve("requests")
            'requests'
            >>> resolver.resolve("cv2")
            'opencv-python'
        """
        # Check cache first
        if import_name in self._cache:
            return self._cache[import_name]

        # Check custom mapping
        if import_name in self._custom_mapping:
            package_name = self._custom_mapping[import_name]
            self._cache[import_name] = package_name
            return package_name

        # Try to resolve via importlib.metadata
        resolved = self._resolve_via_metadata(import_name)
        if resolved:
            self._cache[import_name] = resolved
            return resolved

        # Check built-in mapping for common edge cases
        builtin_mapping = self._get_builtin_mapping()
        if import_name in builtin_mapping:
            package_name = builtin_mapping[import_name]
            self._cache[import_name] = package_name
            return package_name

        # Fallback: assume import name is package name
        self._cache[import_name] = import_name
        return import_name

    def _resolve_via_metadata(self, import_name: str) -> str | None:
        """Resolve package name using importlib.metadata.

        Args:
            import_name: The module name to resolve.

        Returns:
            Package name if found, None otherwise.
        """
        try:
            # Try to get distribution for the top-level module
            top_level = import_name.split(".")[0]

            # Iterate through all distributions to find which one provides this module
            for dist in importlib.metadata.distributions():
                try:
                    # Get top-level modules provided by this distribution
                    if dist.read_text("top_level.txt"):
                        top_levels = dist.read_text("top_level.txt").strip().split("\n")
                        if top_level in top_levels:
                            return dist.metadata["Name"]
                except (FileNotFoundError, KeyError):
                    continue

            return None
        except Exception:
            return None

    def _get_builtin_mapping(self) -> dict[str, str]:
        """Get built-in mapping for common edge cases.

        Returns:
            Dictionary mapping import names to package names.
        """
        return {
            # Computer vision
            "cv2": "opencv-python",
            "cv2.cv2": "opencv-python",
            # Image processing
            "PIL": "Pillow",
            "Image": "Pillow",
            # Scientific
            "sklearn": "scikit-learn",
            "skimage": "scikit-image",
            # YAML
            "yaml": "PyYAML",
            # Date/time
            "dateutil": "python-dateutil",
            # Other common cases
            "attr": "attrs",
            "dotenv": "python-dotenv",
            "magic": "python-magic",
        }

    def load_mapping(self) -> dict[str, str]:
        """Load the complete mapping (custom + builtin).

        Returns:
            Combined mapping dictionary.
        """
        mapping = self._get_builtin_mapping().copy()
        mapping.update(self._custom_mapping)
        return mapping

    def clear_cache(self) -> None:
        """Clear the resolution cache."""
        self._cache.clear()


def resolve_package_name(import_name: str, resolver: PackageResolver | None = None) -> str:
    """Convenience function to resolve a single package name.

    Args:
        import_name: The module name to resolve.
        resolver: Optional PackageResolver instance. If None, creates a new one.

    Returns:
        The PyPI package name.
    """
    if resolver is None:
        resolver = PackageResolver()
    return resolver.resolve(import_name)
