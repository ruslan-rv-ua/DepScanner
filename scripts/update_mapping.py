"""Script to update the package mapping by scanning installed packages.

This script uses importlib.metadata to discover all installed packages
and their top-level modules, generating a mapping that can be used
for package resolution.
"""

import importlib.metadata
from pathlib import Path


def generate_mapping() -> dict[str, str]:
    """Generate mapping from top-level modules to package names.
    
    Returns:
        Dictionary mapping module names to package names.
    """
    mapping: dict[str, str] = {}
    
    for dist in importlib.metadata.distributions():
        try:
            package_name = dist.metadata["Name"]
            
            # Try to read top_level.txt
            top_level_txt = dist.read_text("top_level.txt")
            if top_level_txt:
                top_levels = top_level_txt.strip().split("\n")
                
                for module in top_levels:
                    module = module.strip()
                    if module and module not in mapping:
                        mapping[module] = package_name
        except (FileNotFoundError, KeyError):
            continue
    
    return mapping


def main() -> None:
    """Generate and display the mapping."""
    print("Generating package mapping from installed packages...")
    print()
    
    mapping = generate_mapping()
    
    print(f"Total mappings found: {len(mapping)}")
    print()
    print("Sample mappings (first 20):")
    print("-" * 60)
    
    for i, (module, package) in enumerate(sorted(mapping.items())[:20], 1):
        print(f"{i:2d}. {module:30s} -> {package}")
    
    # Find interesting mappings (where module != package)
    different = {m: p for m, p in mapping.items() if m != p and m.lower() != p.lower()}
    
    print()
    print(f"Mappings where module != package: {len(different)}")
    print("-" * 60)
    
    for i, (module, package) in enumerate(sorted(different.items())[:30], 1):
        print(f"{i:2d}. {module:30s} -> {package}")
    
    # Save to file
    output_file = Path(__file__).parent.parent / "package_mapping.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Package Mapping (Module -> Package Name)\n")
        f.write(f"# Total: {len(mapping)} mappings\n")
        f.write("#" + "=" * 60 + "\n\n")
        
        for module, package in sorted(mapping.items()):
            f.write(f"{module} -> {package}\n")
    
    print()
    print(f"Full mapping saved to: {output_file}")


if __name__ == "__main__":
    main()
