#!/usr/bin/env python3
"""Tests for ObfuscateLLVM CLI."""

import json
import pytest
import subprocess
import tempfile
from pathlib import Path


def test_cli_help():
    """Test CLI help output."""
    result = subprocess.run(
        ["python", "src/cli/obfuscatellvm.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "ObfuscateLLVM" in result.stdout


def test_cli_basic_run():
    """Test basic CLI execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        report_path = Path(tmpdir) / "report.json"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--report", str(report_path),
            "--verbose"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Obfuscation completed successfully!" in result.stdout
        assert report_path.exists()
        
        # Validate report structure
        with open(report_path) as f:
            report = json.load(f)
        
        assert "version" in report
        assert "input" in report
        assert "output" in report
        assert "passes" in report
        assert "metrics" in report


def test_cli_profiles():
    """Test different obfuscation profiles."""
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    
    for profile in profiles:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / f"test_output_{profile}"
            
            result = subprocess.run([
                "python", "src/cli/obfuscatellvm.py",
                "--input", "examples/hello.c",
                "--output", str(output_path),
                "--profile", profile
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert f"Profile: {profile}" in result.stdout


def test_cli_options():
    """Test various CLI options."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        report_path = Path(tmpdir) / "report.json"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--enable-string-encrypt",
            "--junk-density", "0.2",
            "--cycles", "3",
            "--seed", "12345",
            "--embed-watermark", "test@example.com",
            "--no-telemetry",
            "--report", str(report_path)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "String encryption: enabled" in result.stdout
        assert "Junk density: 0.2" in result.stdout
        assert "Cycles: 3" in result.stdout
        assert "Seed: 12345" in result.stdout
        assert "Watermark: test@example.com" in result.stdout
        assert "Telemetry: disabled" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])