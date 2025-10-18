"""Script to generate standard library module lists for different Python versions.

This script can be used to generate stdlib lists for documentation or reference.
In practice, depscanner uses sys.stdlib_module_names at runtime.
"""

import sys
from pathlib import Path


def main() -> None:
    """Generate and print the stdlib module list."""
    print(f"Python version: {sys.version}")
    print(f"Python version info: {sys.version_info}\n")
    
    if hasattr(sys, "stdlib_module_names"):
        stdlib_modules = sorted(sys.stdlib_module_names)
        print(f"Total stdlib modules: {len(stdlib_modules)}\n")
        
        # Print all modules
        print("Standard library modules:")
        print("-" * 50)
        for i, module in enumerate(stdlib_modules, 1):
            print(f"{i:3d}. {module}")
        
        # Save to file
        output_file = Path(__file__).parent.parent / "stdlib_list.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Python {sys.version_info.major}.{sys.version_info.minor} stdlib modules\n")
            f.write(f"Total: {len(stdlib_modules)}\n")
            f.write("=" * 50 + "\n\n")
            for module in stdlib_modules:
                f.write(f"{module}\n")
        
        print(f"\nSaved to: {output_file}")
    else:
        print("ERROR: sys.stdlib_module_names not available.")
        print("This feature requires Python 3.10 or later.")
        sys.exit(1)


if __name__ == "__main__":
    main()
