# ObfuscateLLVM Demo Guide

## Quick Demo Script

This guide provides step-by-step demonstrations of ObfuscateLLVM's key features.

### Prerequisites

```bash
# Using Docker (recommended)
docker build -f docker/dev.Dockerfile -t obfuscatellvm .
docker run -it -v $(pwd):/workspace obfuscatellvm

# Or verify local installation
python tooling/verify-setup.py
```

## Demo 1: Basic Obfuscation

### Step 1: Examine Original Code
```bash
# Look at the example program
cat examples/hello.c
```

**Output:**
```c
#include <stdio.h>
#include <string.h>

const char* greeting = "Hello, ObfuscateLLVM!";
const char* message = "This is a test program for obfuscation.";

int main(int argc, char* argv[]) {
    printf("%s\n", greeting);
    printf("%s\n", message);
    
    if (argc > 1) {
        printf("Arguments provided: %d\n", argc - 1);
        for (int i = 1; i < argc; i++) {
            printf("  Arg %d: %s\n", i, argv[i]);
        }
    }
    
    // Simple computation to test obfuscation
    int sum = 0;
    for (int i = 1; i <= 10; i++) {
        sum += i;
    }
    printf("Sum of 1-10: %d\n", sum);
    
    return 0;
}
```

### Step 2: Basic Obfuscation
```bash
# Apply minimal obfuscation
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_obfuscated \
    --profile minimal \
    --verbose
```

**Expected Output:**
```
ObfuscateLLVM v1.0.0
Input: examples/hello.c
Output: hello_obfuscated
Target: native
Profile: minimal
Junk density: 0.0
Cycles: 1
Running: clang -S -emit-llvm -o /tmp/input.ll examples/hello.c
Running: opt -load-pass-plugin=libobfuscate-passes.so -passes=symbol-rename -S /tmp/input.ll -o /tmp/obfuscated.ll
Running: clang -c /tmp/obfuscated.ll -o /tmp/output.o
Running: clang /tmp/output.o -o hello_obfuscated
Obfuscation completed successfully!
Processing time: 1.23s
Size change: 1247 -> 1298 bytes
```

### Step 3: Test Obfuscated Binary
```bash
# Run original vs obfuscated
clang examples/hello.c -o hello_original
./hello_original test arg

./hello_obfuscated test arg
```

**Both should produce identical output:**
```
Hello, ObfuscateLLVM!
This is a test program for obfuscation.
Arguments provided: 2
  Arg 1: test
  Arg 2: arg
Sum of 1-10: 55
```

## Demo 2: Advanced Obfuscation with Reporting

### Step 1: Maximum Protection
```bash
# Apply maximum obfuscation with HTML report
python src/cli/obfuscatellvm.py \
    --input examples/math.c \
    --output math_protected \
    --profile maximum \
    --cycles 3 \
    --seed 12345 \
    --report math_report.html \
    --embed-watermark "demo@obfuscatellvm.org" \
    --verbose
```

### Step 2: Examine Report
```bash
# Open HTML report in browser
# Or view JSON version
python src/cli/obfuscatellvm.py \
    --input examples/math.c \
    --output math_protected_json \
    --profile maximum \
    --report math_report.json

cat math_report.json
```

**Sample Report:**
```json
{
  "version": "1.0.0",
  "input": "examples/math.c",
  "output": "math_protected",
  "profile": "maximum",
  "passes": {
    "string_encryption": true,
    "junk_insertion": true,
    "symbol_renaming": true
  },
  "metrics": {
    "input_size": 2156,
    "output_size": 4312,
    "strings_encrypted": 8,
    "junk_blocks_added": 15,
    "symbols_renamed": 12,
    "cfg_flattened": 3,
    "functions_virtualized": 2
  },
  "performance": {
    "processing_time_seconds": 4.67
  },
  "watermark": "demo@obfuscatellvm.org"
}
```

## Demo 3: ML-Generated Policy

### Step 1: Train ML Agent
```bash
# Generate ML-optimized policy
python src/cli/ml_policy.py
```

**Output:**
```
Training ML policy generator...
Training completed:
  Episodes: 1000
  Final reward: -1.850
  Average reward: -0.268

Generated policy for math.c:
  Passes: ['decompiler-adversarial', 'symbol-rename', 'opaque-predicates', 'string-encrypt']
  Security score: 0.750
  Performance score: 0.690
  Combined score: 0.726
```

### Step 2: Apply ML Policy
```bash
# Use ML-generated policy
python src/cli/obfuscatellvm.py \
    --input examples/math.c \
    --output math_ml \
    --ml-policy \
    --verbose
```

## Demo 4: Cross-Platform Builds

### Step 1: Windows Target
```bash
# Cross-compile for Windows
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_windows.exe \
    --target windows \
    --profile balanced \
    --verbose
```

### Step 2: Linux Target
```bash
# Explicit Linux target
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_linux \
    --target linux \
    --profile balanced \
    --verbose
```

## Demo 5: Web Interface

### Step 1: Start Web UI
```bash
# Launch web interface
python webui/app.py
```

### Step 2: Interactive Obfuscation
1. Open browser to `http://localhost:5000`
2. Paste code in editor:
```c
#include <stdio.h>
int main() {
    printf("Web UI Demo\n");
    return 0;
}
```
3. Select "Balanced" profile
4. Enable "Control Flow Flattening"
5. Click "Obfuscate Code"
6. View results and CFG comparison

## Demo 6: Profile Marketplace

### Step 1: Search Profiles
```bash
# Search for security profiles
python src/cli/marketplace.py search --query security
```

**Output:**
```
Found 1 profiles:
  enterprise_secure: Enterprise Secure by security_team
    Enterprise-grade security profile with maximum protection
    Downloads: 1250, Rating: 4.8
```

### Step 2: Download Profile
```bash
# Download and install enterprise profile
python src/cli/marketplace.py download enterprise_secure
```

### Step 3: Use Downloaded Profile
```bash
# Use marketplace profile
python src/cli/obfuscatellvm.py \
    --input examples/math.c \
    --output math_enterprise \
    --profile enterprise_secure \
    --verbose
```

## Demo 7: Build Signing and Verification

### Step 1: Signed Build
```bash
# Create signed build with watermark
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_signed \
    --sign-build \
    --embed-watermark "signed-demo@company.com" \
    --verbose
```

### Step 2: Examine Manifest
```bash
# View generated manifest
cat hello_signed.manifest.json
```

**Sample Manifest:**
```json
{
  "manifest": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00Z",
    "input": {
      "file": "examples/hello.c",
      "hash": "a1b2c3d4...",
      "size": 1247
    },
    "output": {
      "file": "hello_signed",
      "hash": "e5f6g7h8...",
      "size": 2156
    },
    "watermark": "signed-demo@company.com"
  },
  "signature": "3a4b5c6d7e8f...",
  "public_key_fingerprint": "9f8e7d6c5b4a"
}
```

### Step 3: Extract Watermark
```bash
# Extract embedded watermark
python -c "
from src.cli.signing import extract_watermark
print('Watermark:', extract_watermark('hello_signed'))
"
```

## Demo 8: Performance Benchmarking

### Step 1: Run Benchmark Suite
```bash
# Comprehensive performance analysis
python tooling/benchmark.py
```

**Sample Output:**
```
Running ObfuscateLLVM Benchmark Suite...
==================================================

Benchmarking profile: minimal
  Testing examples/hello.c...
    Success rate: 100.0%
    Avg time: 1.23s
    Avg size increase: 4.1%

Benchmarking profile: balanced
  Testing examples/hello.c...
    Success rate: 100.0%
    Avg time: 2.45s
    Avg size increase: 48.8%

Benchmarking profile: maximum
  Testing examples/hello.c...
    Success rate: 100.0%
    Avg time: 4.67s
    Avg size increase: 125.3%

Summary:
  Total tests: 24
  Successful tests: 24
  Success rate: 100.0%
```

## Demo 9: Research Features

### Step 1: Symbolic Verification
```bash
# Verify semantic equivalence (requires Z3)
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_verified \
    --verify-equivalence \
    --verbose
```

### Step 2: Decompiler Evaluation
```bash
# Evaluate against decompilers (requires Ghidra/Radare2)
python src/cli/evaluation_harness.py
```

## Demo 10: Safe Mode

### Step 1: AV-Friendly Obfuscation
```bash
# Safe mode to avoid antivirus false positives
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_safe \
    --safe-mode \
    --verbose
```

**Output shows reduced obfuscation:**
```
Safe mode enabled (AV-friendly)
Junk density: 0.05  # Reduced from default
CFG flattening: disabled
Virtualization: disabled
```

## Performance Comparison

### Size Overhead by Profile
| Profile | Size Increase | Runtime Overhead | Security Level |
|---------|---------------|------------------|----------------|
| Minimal | 5-10% | <5% | Low |
| Balanced | 30-50% | 50-100% | Medium |
| Maximum | 100-200% | 200-500% | High |
| AV-Safe | 15-25% | 10-30% | Medium |

### Processing Time by Input Size
| Input Size | Minimal | Balanced | Maximum |
|------------|---------|----------|---------|
| <1KB | 0.5s | 1.2s | 2.8s |
| 1-10KB | 1.2s | 2.5s | 5.4s |
| 10-100KB | 3.1s | 6.8s | 15.2s |

## Troubleshooting Demo Issues

### Common Problems

#### LLVM Tools Not Found
```bash
# Check installation
llvm-config --version
which clang

# Use Docker if tools missing
docker run -it -v $(pwd):/workspace obfuscatellvm
```

#### Permission Errors
```bash
# Fix permissions
chmod +x tooling/*.py
chmod +x src/cli/*.py
```

#### Build Failures
```bash
# Clean and rebuild
rm -rf build/
mkdir build && cd build
cmake .. && make -j$(nproc)
```

## Next Steps

After completing these demos:

1. **Read Documentation**: [User Guide](USER_GUIDE.md), [API Reference](API.md)
2. **Explore Research**: [Research Features](RESEARCH.md)
3. **Contribute**: [Contributing Guidelines](../CONTRIBUTING.md)
4. **Get Support**: GitHub Issues, Community Discussions

## Demo Video Script

For recorded demonstrations, follow this script:

1. **Introduction** (30s): "Welcome to ObfuscateLLVM demonstration"
2. **Basic Usage** (2min): Show simple obfuscation with before/after
3. **Advanced Features** (3min): Profiles, ML policy, cross-platform
4. **Web Interface** (2min): Interactive obfuscation and visualization
5. **Enterprise Features** (2min): Signing, watermarking, marketplace
6. **Conclusion** (30s): Summary and next steps

Total runtime: ~10 minutes