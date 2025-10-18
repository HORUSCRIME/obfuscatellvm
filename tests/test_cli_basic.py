#!/usr/bin/env python3
"""Basic CLI tests that don't require LLVM tools."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_cli_help():
    """Test CLI help output."""
    result = subprocess.run([
        "python", "src/cli/obfuscatellvm.py", "--help"
    ], capture_output=True, text=True, cwd=Path.cwd())
    
    assert result.returncode == 0
    assert "ObfuscateLLVM" in result.stdout
    assert "--input" in result.stdout
    assert "--output" in result.stdout


def test_cli_version_info():
    """Test CLI shows version information."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path)
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "ObfuscateLLVM v1.0.0" in result.stdout


def test_profile_parsing():
    """Test profile option parsing."""
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    
    for profile in profiles:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"
            
            result = subprocess.run([
                "python", "src/cli/obfuscatellvm.py",
                "--input", "examples/hello.c",
                "--output", str(output_path),
                "--profile", profile,
                "--verbose"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            assert f"Profile: {profile}" in result.stdout


def test_report_generation():
    """Test report generation without compilation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        report_path = Path(tmpdir) / "report.json"
        
        # This will fail at compilation but should still show report intent
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--report", str(report_path),
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        # Should show it's trying to generate report
        assert "report" in result.stdout.lower() or "Report" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])