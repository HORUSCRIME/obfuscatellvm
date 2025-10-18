#!/usr/bin/env python3
"""Integration tests for ObfuscateLLVM end-to-end pipeline."""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path


def test_hello_c_obfuscation():
    """Test obfuscation of hello.c example."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "hello_obf"
        report_path = Path(tmpdir) / "report.json"
        
        # Run obfuscation
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--report", str(report_path),
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        assert result.returncode == 0
        assert "Obfuscation completed successfully!" in result.stdout


def test_math_c_obfuscation():
    """Test obfuscation of math.c example."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "math_obf"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/math.c",
            "--output", str(output_path),
            "--profile", "balanced"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert result.returncode == 0


def test_profile_configurations():
    """Test different obfuscation profiles."""
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    
    for profile in profiles:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / f"test_{profile}"
            
            result = subprocess.run([
                "python", "src/cli/obfuscatellvm.py",
                "--input", "examples/hello.c",
                "--output", str(output_path),
                "--profile", profile,
                "--verbose"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            assert result.returncode == 0
            assert f"Profile: {profile}" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])