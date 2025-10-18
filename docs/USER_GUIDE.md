# ObfuscateLLVM User Guide

## Quick Start

### Installation

#### Using Docker (Recommended)
```bash
# Pull the official image
docker pull obfuscatellvm/obfuscatellvm:latest

# Or build from source
git clone https://github.com/obfuscatellvm/obfuscatellvm.git
cd obfuscatellvm
docker build -f docker/dev.Dockerfile -t obfuscatellvm .
```

#### Local Installation
```bash
# Prerequisites: LLVM 16+, CMake 3.20+, Python 3.11+
git clone https://github.com/obfuscatellvm/obfuscatellvm.git
cd obfuscatellvm

# Build LLVM passes
mkdir build && cd build
cmake .. && make -j$(nproc)

# Install Python CLI
pip install -e .
```

### Basic Usage

#### Simple Obfuscation
```bash
# Basic string and symbol obfuscation
obfuscatellvm -i source.c -o protected_binary

# With profile
obfuscatellvm -i source.c -o protected_binary --profile balanced
```

#### Advanced Features
```bash
# Maximum protection with all passes
obfuscatellvm -i source.c -o protected_binary --profile maximum --cycles 3

# ML-generated policy
obfuscatellvm -i source.c -o protected_binary --ml-policy

# Cross-platform with signing
obfuscatellvm -i source.c -o protected.exe --target windows --sign-build
```

## Obfuscation Profiles

### Built-in Profiles

| Profile | Security | Performance | Use Case |
|---------|----------|-------------|----------|
| `minimal` | Low | High | Development, debugging |
| `balanced` | Medium | Medium | General production use |
| `maximum` | High | Low | High-security applications |
| `av-safe` | Medium | High | Avoid antivirus false positives |

### Custom Profiles
```json
{
  "name": "custom_profile",
  "description": "Custom obfuscation configuration",
  "passes": {
    "string_encryption": true,
    "junk_insertion": true,
    "symbol_renaming": true
  },
  "config": {
    "junk_density": 0.15,
    "cycles": 2,
    "cfg_flatten": true,
    "opaque_predicates": true,
    "virtualize": false
  }
}
```

## Command Line Options

### Input/Output
- `--input, -i`: Input C/C++ source file (required)
- `--output, -o`: Output obfuscated binary path (required)
- `--target`: Target platform (`native`, `linux`, `windows`)

### Obfuscation Control
- `--profile`: Use predefined profile (`minimal`, `balanced`, `maximum`, `av-safe`)
- `--cycles`: Number of obfuscation cycles (1-5)
- `--seed`: Deterministic seed for reproducible builds
- `--junk-density`: Junk code density (0.0-1.0)

### Advanced Features
- `--polymorphic`: Enable polymorphic obfuscation
- `--ml-policy`: Use ML-generated obfuscation policy
- `--use-pgo`: Use PGO profile for selective obfuscation
- `--safe-mode`: AV-friendly obfuscation

### Security & Compliance
- `--sign-build`: Sign build with cryptographic manifest
- `--embed-watermark`: Embed user watermark in binary
- `--verify-equivalence`: Verify semantic equivalence

### Reporting
- `--report`: Generate report (JSON or HTML)
- `--verbose, -v`: Enable verbose output
- `--no-telemetry`: Disable usage telemetry

## Web Interface

### Starting the Web UI
```bash
# Start web server
python webui/app.py

# Access at http://localhost:5000
```

### Features
- **Interactive Editor**: Real-time code editing and obfuscation
- **Pass Controls**: Toggle individual obfuscation passes
- **CFG Visualization**: Before/after control flow graphs
- **Metrics Dashboard**: Live performance and security metrics

## Profile Marketplace

### Searching Profiles
```bash
# Search by keyword
obfuscate-marketplace search --query security

# Filter by category
obfuscate-marketplace search --category performance
```

### Installing Profiles
```bash
# Download and install
obfuscate-marketplace download enterprise_secure

# List installed profiles
obfuscate-marketplace list
```

### Sharing Profiles
```bash
# Upload custom profile
obfuscate-marketplace upload my_profile.json --author "user@company.com"
```

## Performance Optimization

### Profile Selection
- **Development**: Use `minimal` profile for fast iteration
- **Testing**: Use `balanced` profile for realistic performance
- **Production**: Use `maximum` or custom profile for security

### PGO Integration
```bash
# Generate profile
clang -fprofile-instr-generate source.c -o profiling_binary
LLVM_PROFILE_FILE=profile.profraw ./profiling_binary
llvm-profdata merge -output=profile.profdata profile.profraw

# Use profile for selective obfuscation
obfuscatellvm -i source.c -o optimized_binary --use-pgo profile.profdata
```

### Performance Monitoring
```bash
# Benchmark different profiles
python tooling/benchmark.py

# Monitor processing time and size overhead
obfuscatellvm -i source.c -o binary --report metrics.json --verbose
```

## Security Best Practices

### Watermarking
```bash
# Embed user identification
obfuscatellvm -i source.c -o binary --embed-watermark "user@company.com"

# Extract watermark
python -c "
from src.cli.signing import extract_watermark
print(extract_watermark('binary'))
"
```

### Build Signing
```bash
# Sign build with manifest
obfuscatellvm -i source.c -o binary --sign-build

# Verify signature
python -c "
from src.cli.signing import BuildSigner
signer = BuildSigner()
# Verification code here
"
```

### Safe Mode
```bash
# AV-friendly obfuscation
obfuscatellvm -i source.c -o binary --safe-mode
```

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check LLVM installation
llvm-config --version

# Verify environment
python tooling/verify-setup.py
```

#### Performance Issues
```bash
# Use fewer cycles
obfuscatellvm -i source.c -o binary --cycles 1

# Reduce junk density
obfuscatellvm -i source.c -o binary --junk-density 0.05
```

#### Antivirus False Positives
```bash
# Use safe mode
obfuscatellvm -i source.c -o binary --safe-mode

# Use AV-safe profile
obfuscatellvm -i source.c -o binary --profile av-safe
```

### Debug Mode
```bash
# Enable verbose logging
obfuscatellvm -i source.c -o binary --verbose

# Generate detailed report
obfuscatellvm -i source.c -o binary --report debug_report.html
```

## Integration

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Obfuscate Binary
  run: |
    obfuscatellvm -i src/main.c -o dist/protected_app \
      --profile balanced \
      --sign-build \
      --report obfuscation_report.json
```

### Build System Integration
```cmake
# CMake integration
add_custom_target(obfuscate
    COMMAND obfuscatellvm -i ${CMAKE_SOURCE_DIR}/src/main.c 
                         -o ${CMAKE_BINARY_DIR}/protected_app
                         --profile balanced
    DEPENDS main.c
)
```

## Advanced Usage

### Research Features
```bash
# ML policy generation
obfuscatellvm -i source.c -o binary --ml-policy --verbose

# Symbolic equivalence verification
obfuscatellvm -i source.c -o binary --verify-equivalence

# Decompiler evaluation
python src/cli/evaluation_harness.py
```

### Custom Pass Development
```cpp
// Custom LLVM pass
class CustomPass : public PassInfoMixin<CustomPass> {
public:
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM);
};
```

## Support

### Documentation
- [Design Document](DESIGN.md) - Technical architecture
- [Research Features](RESEARCH.md) - Advanced capabilities
- [Security Guidelines](SECURITY.md) - Usage policies
- [Contributing Guide](../CONTRIBUTING.md) - Development guidelines

### Community
- GitHub Issues: Bug reports and feature requests
- Discussions: Questions and community support
- Security: security@obfuscatellvm.org

### Commercial Support
- Enterprise licensing and support available
- Custom development and integration services
- Training and consulting

## License

ObfuscateLLVM is released under the MIT License. See [LICENSE](../LICENSE) for details.