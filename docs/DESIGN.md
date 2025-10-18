# ObfuscateLLVM Design Document

## Architecture Overview

ObfuscateLLVM follows a modular pipeline architecture:

```
C/C++ Source → LLVM IR → Obfuscation Passes → Object Code → Linked Binary
```

### Core Components

1. **CLI Driver** (`src/cli/`): Python-based command-line interface
2. **LLVM Passes** (`src/passes/`): C++ obfuscation transformations
3. **Report Generator**: JSON/HTML output with metrics
4. **Build System**: CMake with cross-platform support

## Obfuscation Passes

### Phase 1 - MVP Passes

#### String Encryption Pass
- **Target**: Global string constants in LLVM IR
- **Method**: Replace with encrypted data + runtime decryptor
- **Key Management**: Per-string XOR keys with simple key derivation
- **Runtime**: Minimal decryption stub injected into binary

#### Junk Code Insertion Pass  
- **Target**: Function basic blocks
- **Method**: Insert dead code paths with opaque predicates
- **Density**: Configurable percentage of original code size
- **Preservation**: Maintains original control flow semantics

#### Symbol Renaming Pass
- **Target**: Local symbols and debug metadata
- **Method**: Replace with obfuscated names (random strings)
- **Scope**: Function-local symbols only (preserves ABI)
- **Metadata**: Strips debug info and source location data

### Phase 3 - Advanced Passes

#### Control Flow Flattening
- **Target**: Function control flow graphs
- **Method**: Convert to switch-based dispatcher
- **State Machine**: Each basic block becomes a case
- **Obfuscation**: Randomized case values and dispatcher logic

#### Opaque Predicates
- **Target**: Branch conditions
- **Method**: Replace with mathematically equivalent complex expressions
- **Examples**: `x % 2 == 0` → `(x*x + x) % 2 == 0`
- **Variety**: Multiple predicate templates for diversity

#### Function Virtualization
- **Target**: Cold/small functions (PGO-guided)
- **Method**: Translate to custom bytecode + VM interpreter
- **VM Design**: Stack-based with minimal instruction set
- **Integration**: VM embedded in binary, functions replaced with VM calls

## Configuration System

### Profiles
- **Minimal**: Basic symbol renaming only
- **Balanced**: String encryption + light junk insertion
- **Maximum**: All passes with high intensity
- **AV-Safe**: Techniques that avoid antivirus false positives

### Per-Pass Configuration
```json
{
  "string_encryption": {
    "enabled": true,
    "key_strength": 128,
    "encrypt_debug_strings": false
  },
  "junk_insertion": {
    "density": 0.1,
    "max_depth": 3,
    "opaque_predicates": true
  },
  "symbol_renaming": {
    "preserve_exports": true,
    "name_pattern": "random"
  }
}
```

## Report Generation

### Metrics Collected
- **Size**: Input/output binary sizes
- **Performance**: Obfuscation time, estimated runtime overhead
- **Coverage**: Number of functions/strings/symbols affected
- **Entropy**: Code entropy before/after transformation

### Output Formats
- **JSON**: Machine-readable metrics and metadata
- **HTML**: Interactive visualization with graphs
- **CSV**: Tabular data for analysis tools

## Cross-Platform Support

### Target Platforms
- **Linux**: ELF binaries via clang/lld
- **Windows**: PE binaries via MinGW cross-compilation
- **Future**: macOS Mach-O support

### Build Matrix
- **Native**: Build on target platform
- **Cross**: Linux → Windows via MinGW
- **Docker**: Containerized builds for consistency

## Security Considerations

### Cryptographic Security
- **Random Generation**: Secure PRNG for keys and seeds
- **Key Derivation**: PBKDF2 for deterministic key generation
- **No Hardcoded Secrets**: All keys derived from user input

### Anti-Analysis Features
- **Watermarking**: Embed user identification
- **Tamper Detection**: Optional integrity checks
- **Debug Stripping**: Remove analysis-friendly metadata

### Ethical Safeguards
- **Usage Telemetry**: Optional monitoring of usage patterns
- **Safe Mode**: AV-friendly obfuscation profiles
- **Documentation**: Clear guidelines for legitimate use

## Performance Characteristics

### Target Metrics (Balanced Profile)
- **Size Overhead**: <50% increase
- **Runtime Overhead**: <2x slowdown
- **Obfuscation Time**: <10s for small programs
- **Memory Usage**: <1GB during processing

### Optimization Strategies
- **Incremental Processing**: Process functions independently
- **Parallel Passes**: Multi-threaded where possible
- **Caching**: Reuse analysis results across passes
- **Selective Application**: PGO-guided pass selection

## Extensibility

### Pass Interface
```cpp
class CustomPass : public PassInfoMixin<CustomPass> {
public:
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};
```

### Plugin System
- **Dynamic Loading**: Load passes from shared libraries
- **Registration**: Automatic pass discovery and registration
- **Configuration**: JSON-based pass parameter specification

### API Design
- **Stable ABI**: C-compatible interface for language bindings
- **Versioning**: Semantic versioning with compatibility guarantees
- **Documentation**: Comprehensive API documentation

## Testing Strategy

### Unit Tests
- **Pass Testing**: Individual pass correctness
- **IR Validation**: LLVM IR validity after transformation
- **Mock Testing**: Isolated component testing

### Integration Tests
- **End-to-End**: Source → obfuscated binary pipeline
- **Cross-Platform**: Linux and Windows target validation
- **Performance**: Regression testing for metrics

### Fuzzing
- **Input Fuzzing**: Random C/C++ source generation
- **Configuration Fuzzing**: Random parameter combinations
- **Crash Detection**: Automated crash reporting

## Future Enhancements

### Research Features
- **ML-Guided Obfuscation**: Reinforcement learning for pass selection
- **Decompiler Adversarial**: Target-specific anti-analysis
- **Symbolic Obfuscation**: SMT-based transformation verification

### Enterprise Features
- **License Management**: Usage tracking and enforcement
- **Team Collaboration**: Shared profiles and configurations
- **CI/CD Integration**: Build system plugins

### Performance Improvements
- **LLVM Integration**: Direct API usage vs. command-line tools
- **Incremental Builds**: Only re-obfuscate changed functions
- **Distributed Processing**: Multi-machine obfuscation