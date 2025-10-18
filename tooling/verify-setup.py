#!/usr/bin/env python3
"""Verify ObfuscateLLVM development environment setup."""

import subprocess
import sys
from pathlib import Path


def check_command(cmd: str, version_flag: str = "--version") -> bool:
    """Check if command is available and print version."""
    try:
        result = subprocess.run([cmd, version_flag], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {cmd}: {result.stdout.strip().split()[0]}")
            return True
        else:
            print(f"[FAIL] {cmd}: command failed")
            return False
    except FileNotFoundError:
        print(f"[FAIL] {cmd}: not found")
        return False


def check_python_packages():
    """Check required Python packages."""
    packages = ["click", "jinja2", "pytest"]
    missing = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"[OK] Python package: {package}")
        except ImportError:
            print(f"[FAIL] Python package: {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0


def main():
    """Main verification function."""
    print("ObfuscateLLVM Environment Verification")
    print("=" * 40)
    
    # Check system tools
    tools_ok = True
    tools_ok &= check_command("cmake")
    tools_ok &= check_command("python3")
    tools_ok &= check_command("git")
    
    # Check LLVM tools (may not be available in all environments)
    print("\nLLVM Tools (required for building):")
    llvm_ok = True
    llvm_ok &= check_command("clang")
    llvm_ok &= check_command("llvm-config")
    llvm_ok &= check_command("opt")
    llvm_ok &= check_command("llc")
    
    # Check Python packages
    print("\nPython Packages:")
    packages_ok = check_python_packages()
    
    # Check project structure
    print("\nProject Structure:")
    required_dirs = [
        "src/cli", "src/passes", "tests", "examples", 
        "docs", "ci", "docker", "tooling"
    ]
    
    structure_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"[OK] Directory: {dir_path}")
        else:
            print(f"[FAIL] Directory: {dir_path} (missing)")
            structure_ok = False
    
    # Summary
    print("\n" + "=" * 40)
    if tools_ok and packages_ok and structure_ok:
        print("[OK] Environment setup complete!")
        if not llvm_ok:
            print("[WARN] LLVM tools not found - use Docker for building")
        return 0
    else:
        print("[FAIL] Environment setup incomplete")
        return 1


if __name__ == "__main__":
    sys.exit(main())