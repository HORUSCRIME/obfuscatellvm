#!/usr/bin/env python3
"""Build script for ObfuscateLLVM project."""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """Run command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def build_project(
    build_type: str = "Release",
    target: str = "native",
    jobs: int = 4,
    tests: bool = True
) -> int:
    """Build the project with specified configuration."""
    
    project_root = Path(__file__).parent.parent
    build_dir = project_root / f"build-{target.lower()}"
    build_dir.mkdir(exist_ok=True)
    
    # Configure CMake
    cmake_args = [
        "cmake",
        str(project_root),
        f"-DCMAKE_BUILD_TYPE={build_type}",
        f"-DBUILD_TESTS={'ON' if tests else 'OFF'}"
    ]
    
    if target == "mingw":
        cmake_args.append(f"-DCMAKE_TOOLCHAIN_FILE={project_root}/tooling/mingw-toolchain.cmake")
    
    if run_command(cmake_args, cwd=build_dir) != 0:
        return 1
    
    # Build
    build_args = ["cmake", "--build", ".", f"-j{jobs}"]
    if run_command(build_args, cwd=build_dir) != 0:
        return 1
    
    # Run tests if enabled
    if tests:
        test_args = ["ctest", "--output-on-failure"]
        if run_command(test_args, cwd=build_dir) != 0:
            return 1
    
    print(f"Build completed successfully in {build_dir}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Build ObfuscateLLVM")
    parser.add_argument(
        "--build-type",
        choices=["Debug", "Release", "RelWithDebInfo"],
        default="Release",
        help="CMake build type"
    )
    parser.add_argument(
        "--target",
        choices=["native", "mingw"],
        default="native",
        help="Build target"
    )
    parser.add_argument(
        "--jobs", "-j",
        type=int,
        default=4,
        help="Number of parallel build jobs"
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip building and running tests"
    )
    
    args = parser.parse_args()
    
    return build_project(
        build_type=args.build_type,
        target=args.target,
        jobs=args.jobs,
        tests=not args.no_tests
    )


if __name__ == "__main__":
    sys.exit(main())