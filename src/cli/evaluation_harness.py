#!/usr/bin/env python3
"""Evaluation harness for measuring obfuscation effectiveness against decompilers."""

import subprocess
import tempfile
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class DecompilerEvaluator:
    """Evaluates obfuscation effectiveness against decompilers."""
    
    def __init__(self):
        self.ghidra_available = self._check_ghidra()
        self.radare2_available = self._check_radare2()
        self.results_cache = {}
    
    def _check_ghidra(self) -> bool:
        """Check if Ghidra headless analyzer is available."""
        try:
            # Check for Ghidra headless script
            result = subprocess.run(["analyzeHeadless", "-help"], 
                                  capture_output=True, text=True, timeout=10)
            return "Ghidra" in result.stdout or result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_radare2(self) -> bool:
        """Check if Radare2 is available."""
        try:
            result = subprocess.run(["r2", "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def analyze_with_ghidra(self, binary_path: str, timeout: int = 60) -> Dict[str, Any]:
        """Analyze binary with Ghidra headless analyzer."""
        if not self.ghidra_available:
            return {"error": "Ghidra not available"}
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_dir = Path(tmpdir) / "ghidra_project"
                output_file = Path(tmpdir) / "analysis_output.txt"
                
                # Create Ghidra analysis script
                script_content = """
// Ghidra analysis script
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;

def program = currentProgram
def decompiler = new DecompInterface()
decompiler.openProgram(program)

def functionManager = program.getFunctionManager()
def functions = functionManager.getFunctions(true)

def results = [:]
def totalFunctions = 0
def successfulDecompilations = 0
def totalInstructions = 0
def decompilationErrors = 0

functions.each { function ->
    totalFunctions++
    totalInstructions += function.getBody().getNumAddresses()
    
    try {
        def decompileResults = decompiler.decompileFunction(function, 30, null)
        if (decompileResults.decompileCompleted()) {
            successfulDecompilations++
            def decompiledFunction = decompileResults.getDecompiledFunction()
            if (decompiledFunction != null) {
                def cCode = decompiledFunction.getC()
                // Analyze decompiled code quality
                def lineCount = cCode.split('\\n').length
                def complexity = cCode.count('{') + cCode.count('if') + cCode.count('for')
                
                results[function.getName()] = [
                    'success': true,
                    'lines': lineCount,
                    'complexity': complexity,
                    'readable': lineCount > 0 && !cCode.contains('undefined')
                ]
            }
        } else {
            decompilationErrors++
            results[function.getName()] = ['success': false, 'error': 'decompilation_failed']
        }
    } catch (Exception e) {
        decompilationErrors++
        results[function.getName()] = ['success': false, 'error': e.getMessage()]
    }
}

// Write results
def outputFile = new File('""" + str(output_file) + """')
outputFile.text = groovy.json.JsonBuilder([
    'total_functions': totalFunctions,
    'successful_decompilations': successfulDecompilations,
    'total_instructions': totalInstructions,
    'decompilation_errors': decompilationErrors,
    'success_rate': totalFunctions > 0 ? (successfulDecompilations / totalFunctions) : 0,
    'functions': results
]).toPrettyString()

decompiler.dispose()
"""
                
                script_file = Path(tmpdir) / "analyze.groovy"
                with open(script_file, 'w') as f:
                    f.write(script_content)
                
                # Run Ghidra headless analysis
                cmd = [
                    "analyzeHeadless",
                    str(project_dir),
                    "TempProject",
                    "-import", binary_path,
                    "-postScript", str(script_file),
                    "-deleteProject"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                
                # Read results
                if output_file.exists():
                    with open(output_file) as f:
                        analysis_results = json.loads(f.read())
                    
                    analysis_results["tool"] = "ghidra"
                    analysis_results["binary"] = binary_path
                    return analysis_results
                else:
                    return {
                        "error": "Analysis output not found",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                
        except subprocess.TimeoutExpired:
            return {"error": "Ghidra analysis timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_with_radare2(self, binary_path: str, timeout: int = 30) -> Dict[str, Any]:
        """Analyze binary with Radare2."""
        if not self.radare2_available:
            return {"error": "Radare2 not available"}
        
        try:
            # Radare2 analysis commands
            r2_commands = [
                "aaa",  # Analyze all
                "aflc", # List functions with complexity
                "pdf", # Print disassembly of functions
            ]
            
            cmd = ["r2", "-q", "-c", ";".join(r2_commands), binary_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode != 0:
                return {"error": "Radare2 analysis failed", "stderr": result.stderr}
            
            # Parse output (simplified)
            output_lines = result.stdout.split('\n')
            function_count = len([line for line in output_lines if line.startswith('0x')])
            
            # Simple metrics extraction
            complexity_lines = [line for line in output_lines if 'cc' in line]
            avg_complexity = 0
            if complexity_lines:
                complexities = []
                for line in complexity_lines:
                    match = re.search(r'cc\s+(\d+)', line)
                    if match:
                        complexities.append(int(match.group(1)))
                avg_complexity = sum(complexities) / len(complexities) if complexities else 0
            
            return {
                "tool": "radare2",
                "binary": binary_path,
                "total_functions": function_count,
                "average_complexity": avg_complexity,
                "analysis_success": True,
                "raw_output_lines": len(output_lines)
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Radare2 analysis timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_obfuscation_score(self, original_results: Dict, obfuscated_results: Dict) -> Dict[str, float]:
        """Calculate obfuscation effectiveness score."""
        scores = {}
        
        # Success rate degradation
        orig_success = original_results.get("success_rate", 1.0)
        obf_success = obfuscated_results.get("success_rate", 1.0)
        
        if orig_success > 0:
            success_degradation = (orig_success - obf_success) / orig_success
            scores["success_degradation"] = max(0.0, success_degradation)
        else:
            scores["success_degradation"] = 0.0
        
        # Complexity increase
        orig_complexity = original_results.get("average_complexity", 1.0)
        obf_complexity = obfuscated_results.get("average_complexity", 1.0)
        
        if orig_complexity > 0:
            complexity_increase = (obf_complexity - orig_complexity) / orig_complexity
            scores["complexity_increase"] = max(0.0, complexity_increase)
        else:
            scores["complexity_increase"] = 0.0
        
        # Error rate increase
        orig_errors = original_results.get("decompilation_errors", 0)
        obf_errors = obfuscated_results.get("decompilation_errors", 0)
        orig_total = original_results.get("total_functions", 1)
        obf_total = obfuscated_results.get("total_functions", 1)
        
        orig_error_rate = orig_errors / orig_total if orig_total > 0 else 0
        obf_error_rate = obf_errors / obf_total if obf_total > 0 else 0
        
        scores["error_rate_increase"] = obf_error_rate - orig_error_rate
        
        # Overall obfuscation score (weighted combination)
        overall_score = (
            0.4 * scores["success_degradation"] +
            0.3 * min(1.0, scores["complexity_increase"]) +
            0.3 * min(1.0, scores["error_rate_increase"])
        )
        
        scores["overall_score"] = max(0.0, min(1.0, overall_score))
        
        return scores
    
    def evaluate_obfuscation(self, original_binary: str, obfuscated_binary: str) -> Dict[str, Any]:
        """Evaluate obfuscation effectiveness."""
        
        evaluation_results = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "original_binary": original_binary,
            "obfuscated_binary": obfuscated_binary,
            "tools_used": [],
            "results": {}
        }
        
        # Analyze with available tools
        if self.ghidra_available:
            print("Analyzing with Ghidra...")
            orig_ghidra = self.analyze_with_ghidra(original_binary)
            obf_ghidra = self.analyze_with_ghidra(obfuscated_binary)
            
            evaluation_results["tools_used"].append("ghidra")
            evaluation_results["results"]["ghidra"] = {
                "original": orig_ghidra,
                "obfuscated": obf_ghidra,
                "scores": self.calculate_obfuscation_score(orig_ghidra, obf_ghidra)
            }
        
        if self.radare2_available:
            print("Analyzing with Radare2...")
            orig_r2 = self.analyze_with_radare2(original_binary)
            obf_r2 = self.analyze_with_radare2(obfuscated_binary)
            
            evaluation_results["tools_used"].append("radare2")
            evaluation_results["results"]["radare2"] = {
                "original": orig_r2,
                "obfuscated": obf_r2,
                "scores": self.calculate_obfuscation_score(orig_r2, obf_r2)
            }
        
        # Calculate combined score
        if evaluation_results["results"]:
            all_scores = []
            for tool_results in evaluation_results["results"].values():
                if "scores" in tool_results:
                    all_scores.append(tool_results["scores"]["overall_score"])
            
            if all_scores:
                evaluation_results["combined_score"] = sum(all_scores) / len(all_scores)
            else:
                evaluation_results["combined_score"] = 0.0
        else:
            evaluation_results["error"] = "No decompiler tools available"
            evaluation_results["combined_score"] = 0.0
        
        return evaluation_results


def run_evaluation_suite(test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
    """Run comprehensive evaluation on multiple test cases."""
    
    evaluator = DecompilerEvaluator()
    suite_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tools_available": {
            "ghidra": evaluator.ghidra_available,
            "radare2": evaluator.radare2_available
        },
        "test_cases": [],
        "summary": {}
    }
    
    if not evaluator.ghidra_available and not evaluator.radare2_available:
        suite_results["error"] = "No decompiler tools available"
        return suite_results
    
    scores = []
    
    for i, test_case in enumerate(test_cases):
        print(f"Evaluating test case {i+1}/{len(test_cases)}: {test_case['name']}")
        
        try:
            result = evaluator.evaluate_obfuscation(
                test_case["original"], 
                test_case["obfuscated"]
            )
            result["name"] = test_case["name"]
            suite_results["test_cases"].append(result)
            
            if "combined_score" in result:
                scores.append(result["combined_score"])
                
        except Exception as e:
            suite_results["test_cases"].append({
                "name": test_case["name"],
                "error": str(e)
            })
    
    # Calculate summary statistics
    if scores:
        suite_results["summary"] = {
            "total_cases": len(test_cases),
            "successful_evaluations": len(scores),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "score_std": (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5
        }
    
    return suite_results


if __name__ == "__main__":
    # Demo evaluation
    evaluator = DecompilerEvaluator()
    
    print("Decompiler Evaluation Harness")
    print(f"Ghidra available: {evaluator.ghidra_available}")
    print(f"Radare2 available: {evaluator.radare2_available}")
    
    if not evaluator.ghidra_available and not evaluator.radare2_available:
        print("\nNo decompiler tools available for evaluation")
        print("Install Ghidra: https://ghidra-sre.org/")
        print("Install Radare2: https://rada.re/")
    else:
        print("\nEvaluation harness ready for testing obfuscated binaries")
        print("Use run_evaluation_suite() with test cases to evaluate obfuscation effectiveness")