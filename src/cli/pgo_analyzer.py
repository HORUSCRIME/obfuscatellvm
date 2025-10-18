#!/usr/bin/env python3
"""PGO (Profile-Guided Optimization) analyzer for selective obfuscation."""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Set


def generate_profile(source_path: str, test_inputs: List[str] = None) -> str:
    """Generate PGO profile data for a source file."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Compile with profile generation
        prof_binary = tmp_path / "prof_binary"
        prof_data = tmp_path / "profile.profraw"
        
        cmd = [
            "clang", "-fprofile-instr-generate", 
            "-fcoverage-mapping", source_path, 
            "-o", str(prof_binary)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Profile compilation failed: {result.stderr}")
        
        # Run with test inputs to generate profile
        env = {"LLVM_PROFILE_FILE": str(prof_data)}
        
        if test_inputs:
            for test_input in test_inputs:
                subprocess.run([str(prof_binary)] + test_input.split(), 
                             env=env, capture_output=True)
        else:
            # Run without arguments
            subprocess.run([str(prof_binary)], env=env, capture_output=True)
        
        # Convert to indexed format
        prof_indexed = tmp_path / "profile.profdata"
        cmd = ["llvm-profdata", "merge", "-output", str(prof_indexed), str(prof_data)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Profile merge failed: {result.stderr}")
        
        return str(prof_indexed)


def analyze_hot_cold_functions(source_path: str, profile_path: str) -> Dict[str, List[str]]:
    """Analyze profile to identify hot and cold functions."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Compile with profile use to get optimization remarks
        remarks_file = tmp_path / "remarks.yaml"
        
        cmd = [
            "clang", "-fprofile-instr-use=" + profile_path,
            "-fsave-optimization-record", 
            "-foptimization-record-file=" + str(remarks_file),
            "-c", source_path, "-o", str(tmp_path / "output.o")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Simple heuristic: parse function names from source
        hot_functions = []
        cold_functions = []
        
        with open(source_path) as f:
            content = f.read()
            
        # Extract function names (simple regex-like parsing)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('int ') or line.startswith('void ') or line.startswith('static '):
                if '(' in line and ')' in line:
                    # Extract function name
                    parts = line.split('(')[0].split()
                    if len(parts) >= 2:
                        func_name = parts[-1].strip('*')
                        if func_name != 'main':
                            # Simple heuristic: functions with loops are hot
                            if 'for' in content or 'while' in content:
                                hot_functions.append(func_name)
                            else:
                                cold_functions.append(func_name)
        
        return {
            "hot_functions": hot_functions,
            "cold_functions": cold_functions
        }


def select_virtualization_candidates(
    hot_cold_analysis: Dict[str, List[str]], 
    max_candidates: int = 3
) -> List[str]:
    """Select functions for virtualization based on PGO analysis."""
    
    # Prefer cold functions for virtualization (less performance impact)
    cold_functions = hot_cold_analysis.get("cold_functions", [])
    
    # Select up to max_candidates cold functions
    candidates = cold_functions[:max_candidates]
    
    return candidates


if __name__ == "__main__":
    # Test with example
    try:
        profile_path = generate_profile("examples/math.c", [""])
        analysis = analyze_hot_cold_functions("examples/math.c", profile_path)
        candidates = select_virtualization_candidates(analysis)
        
        print("PGO Analysis Results:")
        print(f"Hot functions: {analysis['hot_functions']}")
        print(f"Cold functions: {analysis['cold_functions']}")
        print(f"Virtualization candidates: {candidates}")
        
    except Exception as e:
        print(f"PGO analysis failed (expected without LLVM tools): {e}")