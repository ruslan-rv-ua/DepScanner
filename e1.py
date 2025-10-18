from depscanner import scan_directory

# Scan the current directory
result = scan_directory(".")

# Generate requirements.txt
with open("requirements.txt", "w") as f:
    for pkg in sorted(result.packages, key=lambda p: p.name):
        if pkg.version:
            f.write(f"{pkg.name}=={pkg.version}\n")
        else:
            f.write(f"{pkg.name}\n")

print(f"Generated requirements.txt with {len(result.packages)} packages")