#!/usr/bin/env python3
"""Phase 4 tests for web UI, marketplace, and enterprise features."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_web_ui_structure():
    """Test web UI files exist and have correct structure."""
    webui_dir = Path("webui")
    assert webui_dir.exists()
    
    # Check main files
    assert (webui_dir / "app.py").exists()
    assert (webui_dir / "templates" / "index.html").exists()
    
    # Check Flask app structure
    app_content = (webui_dir / "app.py").read_text()
    assert "Flask" in app_content
    assert "/api/obfuscate" in app_content
    assert "/api/cfg-diff" in app_content


def test_marketplace_functionality():
    """Test profile marketplace operations."""
    from src.cli.marketplace import ProfileMarketplace
    
    marketplace = ProfileMarketplace()
    
    # Test search
    results = marketplace.search_profiles("security")
    assert len(results) > 0
    assert any("security" in r["tags"] for r in results)
    
    # Test category filtering
    security_profiles = marketplace.search_profiles(category="security")
    assert all(p["category"] == "security" for p in security_profiles)
    
    # Test list installed profiles
    installed = marketplace.list_installed_profiles()
    assert len(installed) >= 4  # At least builtin profiles


def test_build_signing():
    """Test build signing and manifest generation."""
    try:
        from src.cli.signing import BuildSigner
        
        signer = BuildSigner()
        
        # Test key generation
        assert signer.private_key is not None
        assert signer.public_key is not None
        
        # Test fingerprint generation
        fingerprint = signer.get_public_key_fingerprint()
        assert len(fingerprint) == 16
        
        # Test manifest creation with existing file
        config = {"profile": "test", "cycles": 1}
        manifest = signer.create_manifest("examples/hello.c", "test_out", config)
        
        assert "version" in manifest
        assert "timestamp" in manifest
        assert "configuration" in manifest
        
    except ImportError:
        pytest.skip("Cryptography library not available")


def test_safe_mode_cli():
    """Test safe mode CLI option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--safe-mode",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Safe mode: enabled" in result.stdout
        assert "Safe mode enabled (AV-friendly)" in result.stdout


def test_build_signing_cli():
    """Test build signing CLI option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--sign-build",
            "--embed-watermark", "test@example.com",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Build signing: enabled" in result.stdout


def test_marketplace_cli():
    """Test marketplace CLI interface."""
    # Test search command
    result = subprocess.run([
        "python", "src/cli/marketplace.py", "search", "--query", "security"
    ], capture_output=True, text=True, cwd=Path.cwd())
    
    assert result.returncode == 0
    assert "Found" in result.stdout
    assert "enterprise_secure" in result.stdout
    
    # Test list command
    result = subprocess.run([
        "python", "src/cli/marketplace.py", "list"
    ], capture_output=True, text=True, cwd=Path.cwd())
    
    assert result.returncode == 0
    assert "Installed profiles" in result.stdout


def test_enhanced_profiles_with_enterprise_features():
    """Test enhanced profiles include enterprise features."""
    profiles_dir = Path("profiles")
    
    for profile_file in profiles_dir.glob("*.json"):
        with open(profile_file) as f:
            profile_data = json.load(f)
        
        # Check structure
        assert "name" in profile_data
        assert "description" in profile_data
        assert "passes" in profile_data
        assert "config" in profile_data
        
        # Check performance expectations
        if "performance" in profile_data:
            perf = profile_data["performance"]
            assert "expected_size_increase" in perf
            assert "expected_runtime_overhead" in perf


def test_web_ui_api_endpoints():
    """Test web UI API endpoint structure."""
    app_file = Path("webui/app.py")
    content = app_file.read_text()
    
    # Check required endpoints
    assert "@app.route('/api/profiles')" in content
    assert "@app.route('/api/obfuscate'" in content
    assert "@app.route('/api/cfg-diff')" in content
    
    # Check Flask app configuration
    assert "app = Flask(__name__)" in content
    assert "jsonify" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])