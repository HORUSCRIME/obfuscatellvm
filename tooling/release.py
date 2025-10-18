#!/usr/bin/env python3
"""Release packaging script for ObfuscateLLVM."""

import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import List


def run_command(cmd: List[str], cwd: Path = None) -> int:
    """Run command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def create_source_archive(version: str, output_dir: Path):
    """Create source code archive."""
    
    archive_name = f"obfuscatellvm-{version}-src"
    
    # Files to include in source distribution
    include_patterns = [
        "src/**/*.py",
        "src/**/*.cpp", 
        "src/**/*.c",
        "src/**/*.h",
        "webui/**/*",
        "profiles/*.json",
        "examples/*.c",
        "tests/**/*.py",
        "tests/**/*.cpp",
        "tooling/*.py",
        "docker/*",
        "docs/*.md",
        "*.md",
        "*.txt",
        "*.yml",
        "*.yaml",
        "CMakeLists.txt",
        "setup.py",
        "Dockerfile",
        "docker-compose.yml",
        "LICENSE"
    ]
    
    # Create temporary directory
    temp_dir = output_dir / "temp"
    archive_dir = temp_dir / archive_name
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    project_root = Path(__file__).parent.parent
    
    for pattern in include_patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                rel_path = file_path.relative_to(project_root)
                dest_path = archive_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
    
    # Create archives
    tar_path = output_dir / f"{archive_name}.tar.gz"
    zip_path = output_dir / f"{archive_name}.zip"
    
    # Create tar.gz
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(archive_dir, arcname=archive_name)
    
    # Create zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in archive_dir.rglob("*"):
            if file_path.is_file():
                arc_path = file_path.relative_to(temp_dir)
                zip_file.write(file_path, arc_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    print(f"Created source archives:")
    print(f"  {tar_path}")
    print(f"  {zip_path}")


def build_docker_images(version: str):
    """Build and tag Docker images."""
    
    project_root = Path(__file__).parent.parent
    
    # Build main image
    if run_command(["docker", "build", "-t", f"obfuscatellvm/obfuscatellvm:{version}", "."], cwd=project_root) != 0:
        raise RuntimeError("Docker build failed")
    
    # Tag as latest
    run_command(["docker", "tag", f"obfuscatellvm/obfuscatellvm:{version}", "obfuscatellvm/obfuscatellvm:latest"])
    
    print(f"Built Docker images:")
    print(f"  obfuscatellvm/obfuscatellvm:{version}")
    print(f"  obfuscatellvm/obfuscatellvm:latest")


def create_binary_packages(version: str, output_dir: Path):
    """Create binary packages for different platforms."""
    
    project_root = Path(__file__).parent.parent
    
    # Build Linux binary package
    linux_dir = output_dir / f"obfuscatellvm-{version}-linux-x64"
    linux_dir.mkdir(exist_ok=True)
    
    # Copy binaries and libraries (would be built in CI)
    bin_dir = linux_dir / "bin"
    lib_dir = linux_dir / "lib"
    bin_dir.mkdir(exist_ok=True)
    lib_dir.mkdir(exist_ok=True)
    
    # Copy CLI script
    shutil.copy2(project_root / "src/cli/obfuscatellvm.py", bin_dir / "obfuscatellvm")
    
    # Copy profiles and examples
    shutil.copytree(project_root / "profiles", linux_dir / "profiles")
    shutil.copytree(project_root / "examples", linux_dir / "examples")
    
    # Create install script
    install_script = bin_dir / "install.sh"
    with open(install_script, "w") as f:
        f.write("""#!/bin/bash
# ObfuscateLLVM Installation Script

set -e

echo "Installing ObfuscateLLVM..."

# Check dependencies
command -v clang >/dev/null 2>&1 || { echo "Error: clang not found. Please install LLVM 16+." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found. Please install Python 3.11+." >&2; exit 1; }

# Install to /usr/local
sudo cp bin/obfuscatellvm /usr/local/bin/
sudo cp -r lib/* /usr/local/lib/
sudo cp -r profiles /usr/local/share/obfuscatellvm/

echo "ObfuscateLLVM installed successfully!"
echo "Run 'obfuscatellvm --help' to get started."
""")
    install_script.chmod(0o755)
    
    # Create archive
    tar_path = output_dir / f"obfuscatellvm-{version}-linux-x64.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(linux_dir, arcname=f"obfuscatellvm-{version}-linux-x64")
    
    print(f"Created binary package: {tar_path}")


def create_python_package(version: str, output_dir: Path):
    """Create Python wheel package."""
    
    project_root = Path(__file__).parent.parent
    
    # Build wheel
    if run_command(["python3", "setup.py", "bdist_wheel"], cwd=project_root) != 0:
        raise RuntimeError("Python wheel build failed")
    
    # Copy wheel to output directory
    dist_dir = project_root / "dist"
    for wheel_file in dist_dir.glob("*.whl"):
        shutil.copy2(wheel_file, output_dir)
        print(f"Created Python wheel: {output_dir / wheel_file.name}")


def generate_checksums(output_dir: Path):
    """Generate SHA256 checksums for all release files."""
    
    import hashlib
    
    checksum_file = output_dir / "SHA256SUMS"
    
    with open(checksum_file, "w") as f:
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file() and file_path.name != "SHA256SUMS":
                # Calculate SHA256
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as binary_file:
                    for chunk in iter(lambda: binary_file.read(4096), b""):
                        sha256_hash.update(chunk)
                
                checksum = sha256_hash.hexdigest()
                f.write(f"{checksum}  {file_path.name}\n")
    
    print(f"Generated checksums: {checksum_file}")


def create_release_notes(version: str, output_dir: Path):
    """Create release notes."""
    
    release_notes = f"""# ObfuscateLLVM {version} Release Notes

## New Features

### Phase 1 - MVP
- ✅ String encryption with XOR and runtime decryption
- ✅ Junk code insertion with opaque predicates
- ✅ Symbol renaming and debug metadata stripping
- ✅ JSON report generation with comprehensive metrics
- ✅ Linux ELF binary output with LLVM toolchain

### Phase 2 - Cross-Platform & Configuration
- ✅ Windows PE target support via MinGW cross-compilation
- ✅ HTML report generation with interactive visualizations
- ✅ Obfuscation profiles (minimal, balanced, maximum, av-safe)
- ✅ Deterministic builds with seed control
- ✅ Multi-cycle obfuscation support

### Phase 3 - Advanced Passes
- ✅ Control flow flattening with switch-based dispatcher
- ✅ Opaque predicates with mathematical identities
- ✅ Function virtualization with custom VM
- ✅ PGO integration for selective obfuscation
- ✅ Polymorphic mode with variable transformations

### Phase 4 - Enterprise Features
- ✅ Interactive web UI with CFG visualization
- ✅ Profile marketplace with search and download
- ✅ Build signing with RSA manifests
- ✅ User watermarking and identification
- ✅ Safe mode for AV-friendly obfuscation

### Phase 5 - Research Features
- ✅ Decompiler-adversarial patterns targeting Ghidra/Hex-Rays
- ✅ ML-based policy generation using Q-learning
- ✅ Symbolic equivalence checking with Z3/KLEE
- ✅ Evaluation harness for measuring effectiveness

### Phase 6 - Final Release
- ✅ Comprehensive documentation and user guides
- ✅ Docker images and pip packages
- ✅ Release artifacts and demo materials
- ✅ Performance optimization and enterprise deployment

## Installation

### Docker (Recommended)
```bash
docker pull obfuscatellvm/obfuscatellvm:{version}
docker run -it obfuscatellvm/obfuscatellvm:{version}
```

### Python Package
```bash
pip install obfuscatellvm=={version}
```

### Binary Package
```bash
wget https://github.com/obfuscatellvm/obfuscatellvm/releases/download/v{version}/obfuscatellvm-{version}-linux-x64.tar.gz
tar -xzf obfuscatellvm-{version}-linux-x64.tar.gz
cd obfuscatellvm-{version}-linux-x64
sudo ./bin/install.sh
```

## Performance Characteristics

| Profile | Size Increase | Runtime Overhead | Security Level |
|---------|---------------|------------------|----------------|
| Minimal | 5-10% | <5% | Low |
| Balanced | 30-50% | 50-100% | Medium |
| Maximum | 100-200% | 200-500% | High |
| AV-Safe | 15-25% | 10-30% | Medium |

## Breaking Changes

None - this is the initial stable release.

## Known Issues

- Symbolic verification requires Z3/KLEE installation
- Decompiler evaluation requires Ghidra/Radare2
- Cross-compilation requires MinGW-w64 toolchain

## Security Notes

- All builds are signed with RSA-2048 keys
- Watermarking enables user identification and tracking
- Safe mode prevents antivirus false positives
- Telemetry is optional and can be disabled

## Support

- Documentation: https://obfuscatellvm.readthedocs.io/
- Issues: https://github.com/obfuscatellvm/obfuscatellvm/issues
- Security: security@obfuscatellvm.org

## Acknowledgments

Thanks to the LLVM community, security researchers, and all contributors who made this release possible.
"""
    
    notes_file = output_dir / f"RELEASE_NOTES_{version}.md"
    with open(notes_file, "w") as f:
        f.write(release_notes)
    
    print(f"Created release notes: {notes_file}")


def main():
    """Main release packaging function."""
    
    version = "1.0.0"
    output_dir = Path("release") / f"v{version}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating ObfuscateLLVM {version} release...")
    
    try:
        # Create source archives
        create_source_archive(version, output_dir)
        
        # Build Docker images
        build_docker_images(version)
        
        # Create binary packages
        create_binary_packages(version, output_dir)
        
        # Create Python package
        create_python_package(version, output_dir)
        
        # Generate checksums
        generate_checksums(output_dir)
        
        # Create release notes
        create_release_notes(version, output_dir)
        
        print(f"\n✅ Release {version} created successfully!")
        print(f"📁 Release directory: {output_dir}")
        print(f"📦 Release artifacts:")
        
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   {file_path.name} ({size_mb:.1f} MB)")
        
    except Exception as e:
        print(f"❌ Release creation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())