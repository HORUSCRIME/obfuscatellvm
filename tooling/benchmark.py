#!/usr/bin/env python3
"""Benchmarking script for ObfuscateLLVM performance analysis."""

import subprocess
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any


def benchmark_profile(profile: str, input_file: str, iterations: int = 3) -> Dict[str, Any]:
    """Benchmark a specific obfuscation profile."""
    
    results = {
        "profile": profile,
        "input_file": input_file,
        "iterations": iterations,
        "times": [],
        "sizes": [],
        "success_rate": 0
    }
    
    successful_runs = 0
    
    for i in range(iterations):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / f"output_{i}"
            report_path = Path(tmpdir) / f"report_{i}.json"
            
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    "python", "src/cli/obfuscatellvm.py",
                    "--input", input_file,
                    "--output", str(output_path),
                    "--profile", profile,
                    "--report", str(report_path)
                ], capture_output=True, text=True, timeout=60)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                if result.returncode == 0:
                    successful_runs += 1
                    results["times"].append(processing_time)
                    
                    # Get size information from report if available
                    if report_path.exists():
                        with open(report_path) as f:
                            report_data = json.load(f)
                            results["sizes"].append({
                                "input_size": report_data["metrics"]["input_size"],
                                "output_size": report_data["metrics"]["output_size"]
                            })
                
            except subprocess.TimeoutExpired:
                results["times"].append(60.0)  # Timeout
            except Exception as e:
                print(f"Benchmark iteration {i} failed: {e}")
    
    results["success_rate"] = successful_runs / iterations
    
    if results["times"]:
        results["avg_time"] = sum(results["times"]) / len(results["times"])
        results["min_time"] = min(results["times"])
        results["max_time"] = max(results["times"])
    
    if results["sizes"]:
        avg_input = sum(s["input_size"] for s in results["sizes"]) / len(results["sizes"])
        avg_output = sum(s["output_size"] for s in results["sizes"]) / len(results["sizes"])
        results["avg_size_increase"] = ((avg_output - avg_input) / avg_input * 100) if avg_input > 0 else 0
    
    return results


def run_comprehensive_benchmark() -> Dict[str, Any]:
    """Run comprehensive benchmark across all profiles and examples."""
    
    profiles = ["minimal", "balanced", "maximum", "av-safe"]
    examples = ["examples/hello.c", "examples/math.c", "examples/simple_test.c"]
    
    benchmark_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "profiles": {},
        "summary": {}
    }
    
    print("Running ObfuscateLLVM Benchmark Suite...")
    print("=" * 50)
    
    for profile in profiles:
        print(f"\nBenchmarking profile: {profile}")
        benchmark_results["profiles"][profile] = {}
        
        for example in examples:
            if Path(example).exists():
                print(f"  Testing {example}...")
                result = benchmark_profile(profile, example, iterations=2)
                benchmark_results["profiles"][profile][Path(example).stem] = result
                
                if result["success_rate"] > 0:
                    print(f"    Success rate: {result['success_rate']*100:.1f}%")
                    if "avg_time" in result:
                        print(f"    Avg time: {result['avg_time']:.2f}s")
                    if "avg_size_increase" in result:
                        print(f"    Avg size increase: {result['avg_size_increase']:.1f}%")
                else:
                    print(f"    All runs failed (expected without LLVM tools)")
    
    # Generate summary
    total_tests = len(profiles) * len(examples) * 2  # 2 iterations each
    successful_tests = sum(
        sum(
            result.get("success_rate", 0) * 2  # 2 iterations
            for result in profile_results.values()
        )
        for profile_results in benchmark_results["profiles"].values()
    )
    
    benchmark_results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": int(successful_tests),
        "overall_success_rate": successful_tests / total_tests if total_tests > 0 else 0
    }
    
    return benchmark_results


def generate_benchmark_report(results: Dict[str, Any], output_path: str = "benchmark_report.json"):
    """Generate benchmark report."""
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBenchmark report saved to: {output_path}")
    print("\nSummary:")
    print(f"  Total tests: {results['summary']['total_tests']}")
    print(f"  Successful tests: {results['summary']['successful_tests']}")
    print(f"  Success rate: {results['summary']['overall_success_rate']*100:.1f}%")


if __name__ == "__main__":
    results = run_comprehensive_benchmark()
    generate_benchmark_report(results)