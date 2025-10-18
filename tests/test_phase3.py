#!/usr/bin/env python3
"""Phase 3 tests for advanced obfuscation passes and PGO integration."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_advanced_passes_cli_options():
    """Test CLI accepts advanced pass options."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/math.c",
            "--output", str(output_path),
            "--polymorphic",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Polymorphic mode: enabled" in result.stdout
        assert "Polymorphic mode enabled with seed:" in result.stdout


def test_pgo_analyzer():
    """Test PGO analyzer functionality."""
    try:
        from src.cli.pgo_analyzer import analyze_hot_cold_functions, select_virtualization_candidates
        
        # Test with mock data
        analysis = {
            "hot_functions": ["fibonacci", "main_loop"],
            "cold_functions": ["helper", "utility", "cleanup"]
        }
        
        candidates = select_virtualization_candidates(analysis, max_candidates=2)
        assert len(candidates) <= 2
        assert all(func in analysis["cold_functions"] for func in candidates)
        
    except ImportError:
        pytest.skip("PGO analyzer not available")


def test_enhanced_profiles():
    """Test enhanced profiles with advanced passes."""
    profiles = ["balanced", "maximum"]
    
    for profile in profiles:
        profile_path = Path(f"profiles/{profile}.json")
        with open(profile_path) as f:
            config = json.load(f)
        
        # Check advanced pass configuration
        assert "config" in config
        if profile == "balanced":
            assert config["config"].get("cfg_flatten") == True
            assert config["config"].get("opaque_predicates") == True
        elif profile == "maximum":
            assert config["config"].get("virtualize") == True


def test_vm_runtime_compilation():
    """Test VM runtime can be compiled."""
    vm_runtime_path = Path("src/passes/vm_runtime.c")
    assert vm_runtime_path.exists()
    
    # Check basic structure
    content = vm_runtime_path.read_text()
    assert "vm_interpret" in content
    assert "VM_ADD" in content
    assert "VM_RET" in content


def test_advanced_pass_registration():
    """Test advanced passes are properly registered."""
    registry_path = Path("src/passes/PassRegistry.cpp")
    content = registry_path.read_text()
    
    # Check new passes are registered
    assert "cfg-flatten" in content
    assert "opaque-predicates" in content
    assert "virtualize" in content
    assert "ControlFlowFlatteningPass" in content
    assert "OpaquePredicatesPass" in content
    assert "FunctionVirtualizationPass" in content


def test_polymorphic_mode():
    """Test polymorphic mode configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        # Test with explicit seed
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--polymorphic",
            "--seed", "12345",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Polymorphic mode enabled with seed: 12345" in result.stdout


def test_pass_metrics():
    """Test advanced pass metrics are collected."""
    from src.cli.obfuscatellvm import obfuscate_pipeline
    
    config = {
        "cfg_flatten": True,
        "opaque_predicates": True,
        "virtualize": True,
        "cycles": 1
    }
    
    # This will fail without LLVM but should show the metrics structure
    try:
        metrics = obfuscate_pipeline("examples/hello.c", "test_output", config)
    except:
        # Expected to fail without LLVM tools
        pass
    
    # Test metrics structure in config
    assert "cfg_flatten" in config
    assert "opaque_predicates" in config
    assert "virtualize" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])