#!/usr/bin/env python3
"""Phase 5 tests for research features: ML policy, symbolic verification, and evaluation."""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


def test_decompiler_adversarial_pass():
    """Test decompiler adversarial pass structure."""
    pass_file = Path("src/passes/DecompilerAdversarial.cpp")
    assert pass_file.exists()
    
    content = pass_file.read_text()
    assert "DecompilerAdversarialPass" in content
    assert "insertAntiGhidraPattern" in content
    assert "insertAntiHexRaysPattern" in content
    assert "insertUniversalAntiPattern" in content


def test_ml_policy_generator():
    """Test ML policy generator functionality."""
    from src.cli.ml_policy import MLPolicyGenerator, analyze_program_features
    
    # Test feature extraction
    features = analyze_program_features("examples/hello.c")
    assert isinstance(features, dict)
    assert "size" in features
    assert "complexity" in features
    assert all(0 <= v <= 1 for v in features.values())
    
    # Test policy generation
    generator = MLPolicyGenerator()
    policy = generator.generate_policy(features)
    assert isinstance(policy, list)
    assert len(policy) <= 5  # Max 5 passes
    
    # Test policy evaluation
    evaluation = generator.evaluate_policy(policy, features)
    assert "security_score" in evaluation
    assert "performance_score" in evaluation
    assert "combined_score" in evaluation


def test_ml_policy_training():
    """Test ML agent training process."""
    from src.cli.ml_policy import MLPolicyGenerator
    
    generator = MLPolicyGenerator()
    generator.training_episodes = 10  # Quick test
    
    results = generator.train()
    assert "episodes" in results
    assert "final_reward" in results
    assert "average_reward" in results
    assert results["episodes"] == 10


def test_symbolic_checker_structure():
    """Test symbolic equivalence checker structure."""
    from src.cli.symbolic_checker import SymbolicEquivalenceChecker
    
    checker = SymbolicEquivalenceChecker()
    
    # Test availability checks
    assert hasattr(checker, 'z3_available')
    assert hasattr(checker, 'klee_available')
    
    # Test constraint generation
    ir_code = "define i32 @test(i32 %x) { %1 = add i32 %x, 1 ret i32 %1 }"
    constraints = checker.generate_z3_constraints(ir_code)
    assert "declare-fun" in constraints
    assert "assert" in constraints
    assert "check-sat" in constraints


def test_evaluation_harness_structure():
    """Test evaluation harness structure."""
    from src.cli.evaluation_harness import DecompilerEvaluator
    
    evaluator = DecompilerEvaluator()
    
    # Test tool availability checks
    assert hasattr(evaluator, 'ghidra_available')
    assert hasattr(evaluator, 'radare2_available')
    
    # Test score calculation
    original_results = {
        "success_rate": 0.9,
        "average_complexity": 5.0,
        "decompilation_errors": 1,
        "total_functions": 10
    }
    
    obfuscated_results = {
        "success_rate": 0.6,
        "average_complexity": 8.0,
        "decompilation_errors": 4,
        "total_functions": 10
    }
    
    scores = evaluator.calculate_obfuscation_score(original_results, obfuscated_results)
    assert "success_degradation" in scores
    assert "complexity_increase" in scores
    assert "overall_score" in scores
    assert 0 <= scores["overall_score"] <= 1


def test_ml_policy_cli():
    """Test ML policy CLI option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--ml-policy",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "ML policy: enabled" in result.stdout


def test_equivalence_verification_cli():
    """Test equivalence verification CLI option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output"
        
        result = subprocess.run([
            "python", "src/cli/obfuscatellvm.py",
            "--input", "examples/hello.c",
            "--output", str(output_path),
            "--verify-equivalence",
            "--verbose"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        assert "Equivalence verification: enabled" in result.stdout


def test_research_documentation():
    """Test research documentation exists."""
    research_doc = Path("docs/RESEARCH.md")
    assert research_doc.exists()
    
    content = research_doc.read_text()
    assert "Decompiler-Adversarial Obfuscation" in content
    assert "ML-Based Policy Generation" in content
    assert "Symbolic Equivalence Checking" in content
    assert "Evaluation Harness" in content


def test_advanced_pass_registration():
    """Test advanced research passes are registered."""
    registry_file = Path("src/passes/PassRegistry.cpp")
    content = registry_file.read_text()
    
    assert "decompiler-adversarial" in content
    assert "DecompilerAdversarialPass" in content


def test_program_feature_analysis():
    """Test program feature analysis for ML."""
    from src.cli.ml_policy import analyze_program_features
    
    # Test with different example files
    for example in ["examples/hello.c", "examples/math.c"]:
        if Path(example).exists():
            features = analyze_program_features(example)
            
            # Verify feature structure
            expected_features = [
                "size", "complexity", "function_count", "loop_count",
                "branch_count", "performance_critical", "security_level"
            ]
            
            for feature in expected_features:
                assert feature in features
                assert 0 <= features[feature] <= 1


def test_ml_environment():
    """Test ML environment for policy learning."""
    from src.cli.ml_policy import ObfuscationEnvironment
    
    env = ObfuscationEnvironment()
    
    # Test environment setup
    assert len(env.passes) > 0
    assert env.state_size > 0
    assert env.action_size == len(env.passes)
    
    # Test environment step
    state = env.reset()
    assert len(state) == env.state_size
    
    next_state, reward, done = env.step(0)
    assert len(next_state) == env.state_size
    assert isinstance(reward, float)
    assert isinstance(done, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])