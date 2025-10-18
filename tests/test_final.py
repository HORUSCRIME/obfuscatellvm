#!/usr/bin/env python3
"""Final comprehensive tests for complete ObfuscateLLVM system."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_complete_project_structure():
    """Test that all required project files exist."""
    required_files = [
        "README.md", "LICENSE", "setup.py", "Dockerfile", "docker-compose.yml",
        "CMakeLists.txt", "CONTRIBUTING.md",
        "src/cli/obfuscatellvm.py", "src/cli/marketplace.py", "src/cli/ml_policy.py",
        "src/cli/signing.py", "src/cli/symbolic_checker.py", "src/cli/evaluation_harness.py",
        "src/passes/StringEncryption.cpp", "src/passes/DecompilerAdversarial.cpp",
        "webui/app.py", "webui/templates/index.html",
        "docs/USER_GUIDE.md", "docs/API.md", "docs/DEMO.md", "docs/RESEARCH.md",
        "profiles/minimal.json", "profiles/balanced.json", "profiles/maximum.json",
        "examples/hello.c", "examples/math.c",
        "tooling/benchmark.py", "tooling/release.py"
    ]
    
    for file_path in required_files:
        assert Path(file_path).exists(), f"Required file missing: {file_path}"


def test_all_cli_options():
    """Test that CLI accepts all documented options."""
    result = subprocess.run([
        "python", "src/cli/obfuscatellvm.py", "--help"
    ], capture_output=True, text=True, cwd=Path.cwd())
    
    assert result.returncode == 0
    
    # Check all major options are documented
    help_text = result.stdout
    required_options = [
        "--input", "--output", "--target", "--profile", "--cycles", "--seed",
        "--polymorphic", "--ml-policy", "--use-pgo", "--sign-build", "--safe-mode",
        "--verify-equivalence", "--embed-watermark", "--report", "--verbose"
    ]
    
    for option in required_options:
        assert option in help_text, f"Option {option} not in help text"


def test_all_profiles_exist():
    """Test that all documented profiles exist and are valid."""
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    
    for profile in profiles:
        profile_path = Path(f"profiles/{profile}.json")
        assert profile_path.exists(), f"Profile {profile} not found"
        
        with open(profile_path) as f:
            config = json.load(f)
        
        # Validate structure
        assert "name" in config
        assert "description" in config
        assert "passes" in config
        assert "config" in config
        assert config["name"] == profile


def test_example_programs():
    """Test that example programs are valid C code."""
    examples = ["examples/hello.c", "examples/math.c", "examples/simple_test.c"]
    
    for example in examples:
        if Path(example).exists():
            with open(example) as f:
                content = f.read()
            
            # Basic C code validation
            assert "#include" in content
            assert "main" in content
            assert content.count("{") == content.count("}")


def test_documentation_completeness():
    """Test that all documentation files exist and have content."""
    docs = [
        "docs/USER_GUIDE.md", "docs/API.md", "docs/DEMO.md", 
        "docs/RESEARCH.md", "docs/DESIGN.md", "docs/SECURITY.md"
    ]
    
    for doc in docs:
        doc_path = Path(doc)
        assert doc_path.exists(), f"Documentation missing: {doc}"
        
        content = doc_path.read_text()
        assert len(content) > 1000, f"Documentation too short: {doc}"
        assert "ObfuscateLLVM" in content


def test_web_ui_completeness():
    """Test web UI has all required components."""
    # Test Flask app
    app_file = Path("webui/app.py")
    assert app_file.exists()
    
    content = app_file.read_text()
    assert "Flask" in content
    assert "/api/obfuscate" in content
    assert "/api/profiles" in content
    
    # Test HTML template
    template_file = Path("webui/templates/index.html")
    assert template_file.exists()
    
    html_content = template_file.read_text()
    assert "ObfuscateLLVM" in html_content
    assert "obfuscateBtn" in html_content
    assert "cfg-container" in html_content


def test_docker_configuration():
    """Test Docker configuration files."""
    # Test Dockerfile
    dockerfile = Path("Dockerfile")
    assert dockerfile.exists()
    
    content = dockerfile.read_text()
    assert "FROM ubuntu:22.04" in content
    assert "LLVM" in content
    assert "WORKDIR /app" in content
    
    # Test docker-compose
    compose_file = Path("docker-compose.yml")
    assert compose_file.exists()
    
    compose_content = compose_file.read_text()
    assert "obfuscatellvm" in compose_content
    assert "5000:5000" in compose_content


def test_python_package_setup():
    """Test Python package configuration."""
    setup_file = Path("setup.py")
    assert setup_file.exists()
    
    content = setup_file.read_text()
    assert "obfuscatellvm" in content
    assert "version=" in content
    assert "entry_points" in content
    assert "console_scripts" in content


def test_all_pass_implementations():
    """Test that all LLVM passes are implemented."""
    passes = [
        "StringEncryption.cpp", "JunkInsertion.cpp", "SymbolRenaming.cpp",
        "ControlFlowFlattening.cpp", "OpaquePredicates.cpp", 
        "FunctionVirtualization.cpp", "DecompilerAdversarial.cpp"
    ]
    
    for pass_file in passes:
        pass_path = Path(f"src/passes/{pass_file}")
        assert pass_path.exists(), f"Pass implementation missing: {pass_file}"
        
        content = pass_path.read_text()
        assert "PreservedAnalyses" in content
        assert "namespace obfuscate" in content


def test_cli_integration_all_features():
    """Test CLI integration with all major features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        report_path = Path(tmpdir) / "report.html"
        
        # Test comprehensive CLI call
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--profile", "balanced",
            "--cycles", "2",
            "--seed", "12345",
            "--report", str(report_path),
            "--embed-watermark", "test@example.com",
            "--polymorphic",
            "--ml-policy",
            "--safe-mode",
            "--sign-build",
            "--verify-equivalence",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        # Should show all features in verbose output
        assert "Profile: balanced" in result.stdout
        assert "Cycles: 2" in result.stdout
        assert "Seed: 12345" in result.stdout
        assert "Watermark: test@example.com" in result.stdout
        assert "Polymorphic mode: enabled" in result.stdout
        assert "ML policy: enabled" in result.stdout
        assert "Safe mode: enabled" in result.stdout
        assert "Build signing: enabled" in result.stdout
        assert "Equivalence verification: enabled" in result.stdout


def test_marketplace_functionality():
    """Test marketplace system completeness."""
    from src.cli.marketplace import ProfileMarketplace
    
    marketplace = ProfileMarketplace()
    
    # Test search
    results = marketplace.search_profiles("security")
    assert len(results) > 0
    
    # Test installed profiles
    installed = marketplace.list_installed_profiles()
    assert len(installed) >= 4  # Built-in profiles


def test_ml_system_completeness():
    """Test ML system functionality."""
    from src.cli.ml_policy import MLPolicyGenerator, ObfuscationEnvironment
    
    # Test environment
    env = ObfuscationEnvironment()
    assert len(env.passes) > 0
    
    # Test agent
    generator = MLPolicyGenerator()
    generator.training_episodes = 10  # Quick test
    
    results = generator.train()
    assert "episodes" in results
    assert results["episodes"] == 10


def test_research_features_integration():
    """Test research features are properly integrated."""
    # Test symbolic checker
    from src.cli.symbolic_checker import SymbolicEquivalenceChecker
    checker = SymbolicEquivalenceChecker()
    assert hasattr(checker, 'z3_available')
    
    # Test evaluation harness
    from src.cli.evaluation_harness import DecompilerEvaluator
    evaluator = DecompilerEvaluator()
    assert hasattr(evaluator, 'ghidra_available')
    
    # Test signing system
    from src.cli.signing import BuildSigner
    signer = BuildSigner()
    assert signer.private_key is not None


def test_performance_tools():
    """Test performance analysis tools."""
    # Test benchmark script exists
    benchmark_script = Path("tooling/benchmark.py")
    assert benchmark_script.exists()
    
    content = benchmark_script.read_text()
    assert "benchmark_profile" in content
    assert "run_comprehensive_benchmark" in content


def test_release_packaging():
    """Test release packaging system."""
    release_script = Path("tooling/release.py")
    assert release_script.exists()
    
    content = release_script.read_text()
    assert "create_source_archive" in content
    assert "build_docker_images" in content
    assert "create_binary_packages" in content


def test_all_test_suites():
    """Test that all phase test suites exist."""
    test_files = [
        "tests/test_cli_basic.py", "tests/test_phase2.py", 
        "tests/test_phase3.py", "tests/test_phase4.py", 
        "tests/test_phase5.py", "tests/test_final.py"
    ]
    
    for test_file in test_files:
        assert Path(test_file).exists(), f"Test suite missing: {test_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])