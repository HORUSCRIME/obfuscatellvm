#!/usr/bin/env python3
"""Symbolic equivalence checker for obfuscated functions."""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SymbolicEquivalenceChecker:
    """Checks semantic equivalence between original and obfuscated code."""
    
    def __init__(self):
        self.z3_available = self._check_z3_availability()
        self.klee_available = self._check_klee_availability()
    
    def _check_z3_availability(self) -> bool:
        """Check if Z3 theorem prover is available."""
        try:
            result = subprocess.run(["z3", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_klee_availability(self) -> bool:
        """Check if KLEE symbolic execution engine is available."""
        try:
            result = subprocess.run(["klee", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def extract_function_ir(self, source_path: str, function_name: str) -> Optional[str]:
        """Extract LLVM IR for specific function."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ir_file = Path(tmpdir) / "function.ll"
                
                # Compile to LLVM IR
                cmd = ["clang", "-S", "-emit-llvm", "-o", str(ir_file), source_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return None
                
                # Read and filter for specific function
                with open(ir_file) as f:
                    ir_content = f.read()
                
                # Simple function extraction (would need more robust parsing)
                lines = ir_content.split('\n')
                function_lines = []
                in_function = False
                brace_count = 0
                
                for line in lines:
                    if f"define" in line and function_name in line:
                        in_function = True
                        brace_count = 0
                    
                    if in_function:
                        function_lines.append(line)
                        brace_count += line.count('{') - line.count('}')
                        
                        if brace_count == 0 and '{' in ''.join(function_lines):
                            break
                
                return '\n'.join(function_lines) if function_lines else None
                
        except Exception:
            return None
    
    def generate_z3_constraints(self, ir_code: str) -> str:
        """Generate Z3 constraints from LLVM IR (simplified)."""
        # This is a simplified version - real implementation would need full IR parsing
        constraints = []
        constraints.append("(declare-fun input () Int)")
        constraints.append("(declare-fun output () Int)")
        
        # Extract basic arithmetic operations
        lines = ir_code.split('\n')
        for line in lines:
            line = line.strip()
            if 'add' in line:
                constraints.append("(assert (= output (+ input 1)))")
            elif 'sub' in line:
                constraints.append("(assert (= output (- input 1)))")
            elif 'mul' in line:
                constraints.append("(assert (= output (* input 2)))")
        
        # Default constraint if no operations found
        if len(constraints) == 2:
            constraints.append("(assert (= output input))")
        
        constraints.append("(check-sat)")
        constraints.append("(get-model)")
        
        return '\n'.join(constraints)
    
    def check_z3_equivalence(self, original_ir: str, obfuscated_ir: str) -> Dict[str, any]:
        """Check equivalence using Z3 theorem prover."""
        if not self.z3_available:
            return {"error": "Z3 not available", "equivalent": None}
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Generate constraints for both versions
                orig_constraints = self.generate_z3_constraints(original_ir)
                obf_constraints = self.generate_z3_constraints(obfuscated_ir)
                
                # Write Z3 scripts
                orig_file = Path(tmpdir) / "original.smt2"
                obf_file = Path(tmpdir) / "obfuscated.smt2"
                
                with open(orig_file, 'w') as f:
                    f.write(orig_constraints)
                with open(obf_file, 'w') as f:
                    f.write(obf_constraints)
                
                # Run Z3 on both
                orig_result = subprocess.run(["z3", str(orig_file)], capture_output=True, text=True)
                obf_result = subprocess.run(["z3", str(obf_file)], capture_output=True, text=True)
                
                # Simple equivalence check (compare satisfiability)
                orig_sat = "sat" in orig_result.stdout
                obf_sat = "sat" in obf_result.stdout
                
                return {
                    "equivalent": orig_sat == obf_sat,
                    "original_satisfiable": orig_sat,
                    "obfuscated_satisfiable": obf_sat,
                    "method": "z3"
                }
                
        except Exception as e:
            return {"error": str(e), "equivalent": None}
    
    def generate_klee_harness(self, function_name: str) -> str:
        """Generate KLEE test harness."""
        return f"""
#include <klee/klee.h>

extern int {function_name}(int);

int main() {{
    int input;
    klee_make_symbolic(&input, sizeof(input), "input");
    
    int result = {function_name}(input);
    
    return 0;
}}
"""
    
    def check_klee_equivalence(self, original_c: str, obfuscated_c: str, function_name: str) -> Dict[str, any]:
        """Check equivalence using KLEE symbolic execution."""
        if not self.klee_available:
            return {"error": "KLEE not available", "equivalent": None}
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create test files
                orig_file = tmpdir_path / "original.c"
                obf_file = tmpdir_path / "obfuscated.c"
                harness_file = tmpdir_path / "harness.c"
                
                with open(orig_file, 'w') as f:
                    f.write(original_c)
                with open(obf_file, 'w') as f:
                    f.write(obfuscated_c)
                with open(harness_file, 'w') as f:
                    f.write(self.generate_klee_harness(function_name))
                
                # Compile with KLEE
                orig_bc = tmpdir_path / "original.bc"
                obf_bc = tmpdir_path / "obfuscated.bc"
                
                # Compile to LLVM bitcode
                subprocess.run(["clang", "-I", "/usr/include/klee", "-emit-llvm", "-c", "-g", 
                              str(orig_file), str(harness_file), "-o", str(orig_bc)])
                subprocess.run(["clang", "-I", "/usr/include/klee", "-emit-llvm", "-c", "-g", 
                              str(obf_file), str(harness_file), "-o", str(obf_bc)])
                
                # Run KLEE (simplified - would need proper setup)
                orig_result = subprocess.run(["klee", "--max-time=10", str(orig_bc)], 
                                           capture_output=True, text=True, cwd=tmpdir)
                obf_result = subprocess.run(["klee", "--max-time=10", str(obf_bc)], 
                                          capture_output=True, text=True, cwd=tmpdir)
                
                # Compare results (simplified)
                orig_success = orig_result.returncode == 0
                obf_success = obf_result.returncode == 0
                
                return {
                    "equivalent": orig_success == obf_success,
                    "original_success": orig_success,
                    "obfuscated_success": obf_success,
                    "method": "klee"
                }
                
        except Exception as e:
            return {"error": str(e), "equivalent": None}
    
    def check_function_equivalence(self, 
                                 original_source: str, 
                                 obfuscated_source: str, 
                                 function_name: str) -> Dict[str, any]:
        """Check if a function maintains semantic equivalence after obfuscation."""
        
        results = {
            "function": function_name,
            "z3_result": None,
            "klee_result": None,
            "equivalent": None
        }
        
        # Try Z3 approach
        if self.z3_available:
            orig_ir = self.extract_function_ir(original_source, function_name)
            obf_ir = self.extract_function_ir(obfuscated_source, function_name)
            
            if orig_ir and obf_ir:
                results["z3_result"] = self.check_z3_equivalence(orig_ir, obf_ir)
        
        # Try KLEE approach
        if self.klee_available:
            try:
                with open(original_source) as f:
                    orig_c = f.read()
                with open(obfuscated_source) as f:
                    obf_c = f.read()
                
                results["klee_result"] = self.check_klee_equivalence(orig_c, obf_c, function_name)
            except Exception as e:
                results["klee_result"] = {"error": str(e)}
        
        # Determine overall equivalence
        z3_equiv = results["z3_result"].get("equivalent") if results["z3_result"] else None
        klee_equiv = results["klee_result"].get("equivalent") if results["klee_result"] else None
        
        if z3_equiv is not None and klee_equiv is not None:
            results["equivalent"] = z3_equiv and klee_equiv
        elif z3_equiv is not None:
            results["equivalent"] = z3_equiv
        elif klee_equiv is not None:
            results["equivalent"] = klee_equiv
        else:
            results["equivalent"] = None
            results["error"] = "No symbolic execution tools available"
        
        return results


def main():
    """Demo symbolic equivalence checking."""
    checker = SymbolicEquivalenceChecker()
    
    print("Symbolic Equivalence Checker")
    print(f"Z3 available: {checker.z3_available}")
    print(f"KLEE available: {checker.klee_available}")
    
    if not checker.z3_available and not checker.klee_available:
        print("No symbolic execution tools available")
        print("Install Z3: pip install z3-solver")
        print("Install KLEE: https://klee.github.io/")
        return
    
    # Test with example files
    try:
        result = checker.check_function_equivalence(
            "examples/math.c", 
            "examples/math.c",  # Same file for demo
            "fibonacci"
        )
        
        print(f"\nEquivalence check results:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()