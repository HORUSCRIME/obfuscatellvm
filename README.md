# ObfuscateLLVM

A production-quality LLVM-based binary obfuscator that transforms C/C++ source code through configurable obfuscation passes to produce hardened ELF (Linux) and PE (Windows) binaries.

## Features

- **Modular Obfuscation Passes**: String encryption, junk code insertion, symbol renaming, control-flow flattening, opaque predicates, and function virtualization
- **Cross-Platform**: Supports Linux (ELF) and Windows (PE) targets
- **Configurable Profiles**: Minimal, balanced, maximum, and AV-safe presets
- **Detailed Reporting**: JSON and HTML reports with metrics and visualizations
- **Reproducible Builds**: Deterministic obfuscation with seed control
- **PGO Integration**: Profile-guided optimization for selective protection
- **Web UI**: Interactive visualization of obfuscation results

## Quick Start

### Using Docker (Recommended)

```bash
# Build development environment
docker build -f docker/dev.Dockerfile -t obfuscatellvm-dev .

# Run interactive container
docker run -it -v $(pwd):/workspace obfuscatellvm-dev

# Inside container - build project
cd /workspace
mkdir build && cd build
cmake ..
make -j$(nproc)

# Run obfuscator on sample
cd ..
python src/cli/obfuscatellvm.py --input examples/hello.c --output hello_obf --report report.json
```

### Local Build Requirements

- LLVM 16+ (clang, opt, llc, lld)
- CMake 3.20+
- Python 3.11+
- MinGW-w64 (for Windows cross-compilation)

## Usage

```bash
# Basic obfuscation
python src/cli/obfuscatellvm.py --input source.c --output obfuscated_binary

# With profile and custom settings
python src/cli/obfuscatellvm.py --input source.c --profile balanced --cycles 3 --seed 12345

# Generate detailed report
python src/cli/obfuscatellvm.py --input source.c --report report.html --embed-watermark "user@company.com"
```

## Security & Ethics

This tool is designed for legitimate software protection purposes. See [SECURITY.md](docs/SECURITY.md) for usage guidelines and ethical considerations.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.