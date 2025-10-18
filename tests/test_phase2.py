#!/usr/bin/env python3
"""Phase 2 tests for cross-platform and HTML reporting features."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_html_report_generation():
    """Test HTML report generation from JSON data."""
    from src.cli.report_generator import generate_html_report
    
    # Test data
    report_data = {
        "version": "1.0.0",
        "input": "test.c",
        "output": "test_obf",
        "target": "native",
        "profile": "balanced",
        "passes": {
            "string_encryption": True,
            "junk_insertion": True,
            "symbol_renaming": True
        },
        "config": {
            "junk_density": 0.1,
            "cycles": 2,
            "seed": 12345
        },
        "metrics": {
            "input_size": 1000,
            "output_size": 1500,
            "strings_encrypted": 3,
            "junk_blocks_added": 5,
            "symbols_renamed": 8
        },
        "performance": {
            "processing_time_seconds": 1.5
        },
        "watermark": "test@example.com",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        generate_html_report(report_data, f.name)
        
        # Check file was created and has content
        html_path = Path(f.name)
        assert html_path.exists()
        
        content = html_path.read_text()
        assert "ObfuscateLLVM Report" in content
        assert "test.c" in content
        assert "balanced" in content
        assert "50.0%" in content  # Size increase
        assert "test@example.com" in content


def test_profile_configurations():
    """Test profile configuration loading."""
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    
    for profile in profiles:
        profile_path = Path(f"profiles/{profile}.json")
        assert profile_path.exists(), f"Profile {profile} not found"
        
        with open(profile_path) as f:
            config = json.load(f)
        
        assert "name" in config
        assert "description" in config
        assert "passes" in config
        assert "config" in config
        assert config["name"] == profile


def test_cross_platform_targets():
    """Test cross-platform target parsing."""
    targets = ["native", "linux", "windows"]
    
    for target in targets:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"
            
            result = subprocess.run([
                "python", "src/cli/obfuscatellvm.py",
                "--input", "examples/hello.c",
                "--output", str(output_path),
                "--target", target,
                "--verbose"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            # Should show target in output
            assert f"Target: {target}" in result.stdout


def test_cycles_and_seed_options():
    """Test cycles and seed configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--cycles", "3",
            "--seed", "42",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Cycles: 3" in result.stdout
        assert "Seed: 42" in result.stdout


def test_enhanced_profiles():
    """Test enhanced profile system with JSON configs."""
    from src.cli.obfuscatellvm import get_profile_config
    
    # Test each profile
    minimal = get_profile_config("minimal")
    assert minimal["string_encrypt"] == False
    assert minimal["cycles"] == 1
    
    balanced = get_profile_config("balanced")
    assert balanced["string_encrypt"] == True
    assert balanced["cycles"] == 2
    
    maximum = get_profile_config("maximum")
    assert maximum["junk_density"] == 0.3
    assert maximum["cycles"] == 3
    
    av_safe = get_profile_config("av-safe")
    assert av_safe["junk_density"] == 0.05
    assert av_safe["cycles"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])