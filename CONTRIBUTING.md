# Contributing to ObfuscateLLVM

## Development Environment

### Using Docker (Recommended)
```bash
docker build -f docker/dev.Dockerfile -t obfuscatellvm-dev .
docker run -it -v $(pwd):/workspace obfuscatellvm-dev
```

### Local Setup
- LLVM 16+ with development headers
- CMake 3.20+
- Python 3.11+ with pip
- MinGW-w64 for cross-compilation

## Coding Standards

### C++ (LLVM Passes)
- **Standard**: C++17
- **Style**: LLVM coding standards
- **Formatting**: clang-format with LLVM style
- **Documentation**: Doxygen comments for public APIs
- **Memory**: RAII, smart pointers, no raw new/delete
- **Error Handling**: llvm::Error and llvm::Expected

```cpp
// Example pass structure
class StringEncryptionPass : public PassInfoMixin<StringEncryptionPass> {
public:
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};
```

### Python (CLI/Tools)
- **Standard**: Python 3.11+
- **Style**: PEP 8, enforced by black
- **Type Hints**: Required for all functions
- **Documentation**: Google-style docstrings
- **Testing**: pytest with >90% coverage
- **CLI**: Click framework for argument parsing

```python
def obfuscate_binary(
    input_path: Path,
    output_path: Path,
    passes: List[str],
    config: ObfuscationConfig
) -> ObfuscationReport:
    """Obfuscate binary with specified passes."""
```

## Testing Requirements

### Unit Tests
- All passes must have unit tests
- Test both positive and negative cases
- Use LLVM's testing utilities for IR validation
- Mock external dependencies

### Integration Tests
- End-to-end pipeline tests
- Cross-platform binary execution
- Performance regression tests
- Report generation validation

### Test Commands
```bash
# C++ tests
cd build && ctest --output-on-failure

# Python tests  
pytest tests/ -v --cov=src/cli

# Format check
black --check src/cli/
clang-format --dry-run src/passes/**/*.cpp
```

## Pull Request Process

1. **Branch Naming**: `feature/description` or `fix/issue-number`
2. **Commits**: Atomic, descriptive messages
3. **Testing**: All tests must pass
4. **Documentation**: Update relevant docs
5. **Review**: At least one maintainer approval

### PR Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CI passes
- [ ] Performance impact assessed
- [ ] Security implications reviewed

## Security Guidelines

### Code Security
- No hardcoded secrets or keys
- Input validation for all user data
- Secure random number generation
- Memory safety (bounds checking)

### Obfuscation Ethics
- Include usage warnings in documentation
- Implement telemetry opt-out
- Provide legitimate use case examples
- Avoid techniques that trigger AV false positives

## Performance Standards

### Build Performance
- CMake configure: <30s
- Full build: <5min on CI
- Incremental build: <30s

### Runtime Performance
- Obfuscation time: <10s for small programs
- Memory usage: <1GB for typical workloads
- Binary size increase: <50% for balanced profile

## Documentation Standards

### Code Documentation
- All public APIs documented
- Complex algorithms explained
- Usage examples provided
- Performance characteristics noted

### User Documentation
- Clear installation instructions
- Comprehensive usage examples
- Troubleshooting guides
- Security best practices

## Release Process

### Version Numbering
- Semantic versioning (MAJOR.MINOR.PATCH)
- Pre-release: alpha, beta, rc suffixes
- Git tags for all releases

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Performance benchmarks run
- [ ] Security review completed
- [ ] Cross-platform artifacts built
- [ ] Release notes written

## Issue Reporting

### Bug Reports
- Minimal reproduction case
- Environment details (OS, LLVM version)
- Expected vs actual behavior
- Relevant logs/error messages

### Feature Requests
- Clear use case description
- Proposed API/interface
- Implementation complexity estimate
- Backward compatibility impact

## Community Guidelines

- Be respectful and inclusive
- Focus on technical merit
- Provide constructive feedback
- Help newcomers learn
- Follow the code of conduct

## Getting Help

- GitHub Issues for bugs/features
- Discussions for questions
- Security issues: security@obfuscatellvm.org
- Documentation: docs/ directory