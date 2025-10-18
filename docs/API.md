# ObfuscateLLVM API Reference

## Python CLI API

### Core Functions

#### `obfuscate_pipeline(input_path, output_path, config, target, seed, verbose)`

Main obfuscation pipeline function.

**Parameters:**
- `input_path` (str): Path to input C/C++ source file
- `output_path` (str): Path for output obfuscated binary
- `config` (Dict[str, Any]): Obfuscation configuration
- `target` (str): Target platform ('native', 'linux', 'windows')
- `seed` (Optional[int]): Deterministic seed for reproducibility
- `verbose` (bool): Enable verbose logging

**Returns:**
- `Dict[str, Any]`: Metrics including file sizes, pass statistics

**Example:**
```python
from src.cli.obfuscatellvm import obfuscate_pipeline

config = {
    "string_encrypt": True,
    "junk_density": 0.1,
    "cycles": 2,
    "cfg_flatten": True
}

metrics = obfuscate_pipeline(
    "source.c", 
    "obfuscated_binary", 
    config, 
    "native", 
    12345, 
    True
)
```

#### `get_profile_config(profile_name)`

Load configuration from predefined profile.

**Parameters:**
- `profile_name` (str): Profile name ('minimal', 'balanced', 'maximum', 'av-safe')

**Returns:**
- `Dict[str, Any]`: Profile configuration

**Example:**
```python
from src.cli.obfuscatellvm import get_profile_config

config = get_profile_config("balanced")
print(config["junk_density"])  # 0.1
```

### Report Generation

#### `generate_html_report(report_data, output_path)`

Generate HTML report from obfuscation data.

**Parameters:**
- `report_data` (Dict[str, Any]): Report data structure
- `output_path` (str): Output HTML file path

**Example:**
```python
from src.cli.report_generator import generate_html_report

report_data = {
    "version": "1.0.0",
    "input": "source.c",
    "metrics": {"input_size": 1000, "output_size": 1500},
    "performance": {"processing_time_seconds": 2.5}
}

generate_html_report(report_data, "report.html")
```

### ML Policy Generation

#### `MLPolicyGenerator`

Machine learning-based policy generator.

**Methods:**

##### `train()`
Train the ML agent for policy generation.

**Returns:**
- `Dict[str, Any]`: Training results and metrics

##### `generate_policy(program_features)`
Generate obfuscation policy for given program.

**Parameters:**
- `program_features` (Dict[str, float]): Program characteristics

**Returns:**
- `List[str]`: Selected obfuscation passes

**Example:**
```python
from src.cli.ml_policy import MLPolicyGenerator, analyze_program_features

generator = MLPolicyGenerator()
generator.train()

features = analyze_program_features("source.c")
policy = generator.generate_policy(features)
print(policy)  # ['string-encrypt', 'cfg-flatten', ...]
```

### Build Signing

#### `BuildSigner`

Cryptographic signing for obfuscated builds.

**Methods:**

##### `create_signed_manifest(input_file, output_file, config, watermark)`
Create and sign build manifest.

**Parameters:**
- `input_file` (str): Input source file path
- `output_file` (str): Output binary file path
- `config` (Dict[str, Any]): Obfuscation configuration
- `watermark` (Optional[str]): User watermark

**Returns:**
- `Dict[str, Any]`: Signed manifest with signature

**Example:**
```python
from src.cli.signing import BuildSigner

signer = BuildSigner()
manifest = signer.create_signed_manifest(
    "source.c", 
    "binary", 
    {"profile": "balanced"}, 
    "user@company.com"
)
```

### Symbolic Verification

#### `SymbolicEquivalenceChecker`

Semantic equivalence verification using symbolic execution.

**Methods:**

##### `check_function_equivalence(original_source, obfuscated_source, function_name)`
Verify function equivalence between original and obfuscated versions.

**Parameters:**
- `original_source` (str): Original source file path
- `obfuscated_source` (str): Obfuscated source file path  
- `function_name` (str): Function name to verify

**Returns:**
- `Dict[str, Any]`: Verification results

**Example:**
```python
from src.cli.symbolic_checker import SymbolicEquivalenceChecker

checker = SymbolicEquivalenceChecker()
result = checker.check_function_equivalence(
    "original.c", 
    "obfuscated.c", 
    "main"
)
print(result["equivalent"])  # True/False/None
```

### Evaluation Harness

#### `DecompilerEvaluator`

Automated evaluation against decompiler tools.

**Methods:**

##### `evaluate_obfuscation(original_binary, obfuscated_binary)`
Evaluate obfuscation effectiveness.

**Parameters:**
- `original_binary` (str): Original binary path
- `obfuscated_binary` (str): Obfuscated binary path

**Returns:**
- `Dict[str, Any]`: Evaluation results with scores

**Example:**
```python
from src.cli.evaluation_harness import DecompilerEvaluator

evaluator = DecompilerEvaluator()
results = evaluator.evaluate_obfuscation("orig.exe", "obf.exe")
print(results["combined_score"])  # 0.0-1.0
```

### Profile Marketplace

#### `ProfileMarketplace`

Profile sharing and marketplace operations.

**Methods:**

##### `search_profiles(query, category)`
Search marketplace for profiles.

**Parameters:**
- `query` (str): Search query
- `category` (str): Category filter

**Returns:**
- `List[Dict[str, Any]]`: Search results

##### `download_profile(profile_id, install)`
Download profile from marketplace.

**Parameters:**
- `profile_id` (str): Profile identifier
- `install` (bool): Install locally

**Returns:**
- `Dict[str, Any]`: Download result

**Example:**
```python
from src.cli.marketplace import ProfileMarketplace

marketplace = ProfileMarketplace()
results = marketplace.search_profiles("security", "enterprise")
marketplace.download_profile("enterprise_secure", True)
```

## C++ LLVM Pass API

### Base Pass Interface

All obfuscation passes inherit from LLVM's `PassInfoMixin`:

```cpp
class CustomPass : public llvm::PassInfoMixin<CustomPass> {
public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};
```

### Available Passes

#### String Encryption Pass
- **Name**: `string-encrypt`
- **Type**: Module Pass
- **Function**: Encrypts global string constants with XOR

#### Junk Insertion Pass
- **Name**: `junk-insert`
- **Type**: Function Pass
- **Function**: Inserts dead code blocks with opaque predicates

#### Symbol Renaming Pass
- **Name**: `symbol-rename`
- **Type**: Module Pass
- **Function**: Renames internal symbols and strips debug info

#### Control Flow Flattening Pass
- **Name**: `cfg-flatten`
- **Type**: Function Pass
- **Function**: Converts CFG to switch-based dispatcher

#### Opaque Predicates Pass
- **Name**: `opaque-predicates`
- **Type**: Function Pass
- **Function**: Replaces conditions with complex expressions

#### Function Virtualization Pass
- **Name**: `virtualize`
- **Type**: Module Pass
- **Function**: Converts functions to bytecode with VM

#### Decompiler Adversarial Pass
- **Name**: `decompiler-adversarial`
- **Type**: Function Pass
- **Function**: Inserts anti-decompiler patterns

### Pass Registration

```cpp
// Register with LLVM pass manager
llvm::PassPluginLibraryInfo getObfuscatePassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "ObfuscatePasses", LLVM_VERSION_STRING,
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, ModulePassManager &MPM, ...) {
          if (Name == "string-encrypt") {
            MPM.addPass(obfuscate::StringEncryptionPass());
            return true;
          }
          return false;
        });
    }
  };
}
```

## Web API

### REST Endpoints

#### `GET /api/profiles`
Get available obfuscation profiles.

**Response:**
```json
{
  "minimal": {
    "name": "minimal",
    "description": "Basic obfuscation",
    "passes": {...}
  }
}
```

#### `POST /api/obfuscate`
Run obfuscation with parameters.

**Request:**
```json
{
  "source_code": "int main() { return 0; }",
  "profile": "balanced",
  "cycles": 2,
  "seed": 12345
}
```

**Response:**
```json
{
  "success": true,
  "report": {
    "metrics": {...},
    "performance": {...}
  }
}
```

#### `GET /api/cfg-diff`
Get CFG comparison data.

**Response:**
```json
{
  "original": {
    "nodes": [...],
    "edges": [...]
  },
  "obfuscated": {
    "nodes": [...],
    "edges": [...]
  }
}
```

## Configuration Schema

### Profile Configuration
```json
{
  "name": "string",
  "description": "string",
  "passes": {
    "string_encryption": "boolean",
    "junk_insertion": "boolean",
    "symbol_renaming": "boolean"
  },
  "config": {
    "junk_density": "number (0.0-1.0)",
    "cycles": "integer (1-5)",
    "cfg_flatten": "boolean",
    "opaque_predicates": "boolean",
    "virtualize": "boolean"
  },
  "performance": {
    "expected_size_increase": "string",
    "expected_runtime_overhead": "string"
  }
}
```

### Report Schema
```json
{
  "version": "string",
  "input": "string",
  "output": "string",
  "target": "string",
  "profile": "string",
  "passes": {
    "string_encryption": "boolean",
    "junk_insertion": "boolean",
    "symbol_renaming": "boolean"
  },
  "config": {
    "junk_density": "number",
    "cycles": "integer",
    "seed": "integer"
  },
  "metrics": {
    "input_size": "integer",
    "output_size": "integer",
    "strings_encrypted": "integer",
    "junk_blocks_added": "integer",
    "symbols_renamed": "integer"
  },
  "performance": {
    "processing_time_seconds": "number"
  },
  "watermark": "string",
  "timestamp": "string (ISO 8601)"
}
```

## Error Handling

### Exception Types

#### `RuntimeError`
Raised for compilation or linking failures.

#### `FileNotFoundError`
Raised when input files are missing.

#### `ValueError`
Raised for invalid configuration parameters.

### Error Response Format
```json
{
  "error": "Error description",
  "details": "Additional error details",
  "code": "ERROR_CODE"
}
```

## Examples

### Complete Workflow
```python
import json
from src.cli.obfuscatellvm import obfuscate_pipeline, get_profile_config
from src.cli.report_generator import generate_html_report
from src.cli.signing import BuildSigner

# Load configuration
config = get_profile_config("balanced")
config["cycles"] = 3

# Run obfuscation
metrics = obfuscate_pipeline(
    "source.c", 
    "protected_binary", 
    config, 
    "native", 
    12345, 
    True
)

# Generate report
report_data = {
    "version": "1.0.0",
    "input": "source.c",
    "output": "protected_binary",
    "metrics": metrics,
    "config": config
}

generate_html_report(report_data, "report.html")

# Sign build
signer = BuildSigner()
manifest = signer.create_signed_manifest(
    "source.c", 
    "protected_binary", 
    config, 
    "user@company.com"
)

with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

### Batch Processing
```python
import os
from pathlib import Path

source_dir = Path("src")
output_dir = Path("protected")
config = get_profile_config("maximum")

for source_file in source_dir.glob("*.c"):
    output_file = output_dir / source_file.stem
    
    try:
        metrics = obfuscate_pipeline(
            str(source_file),
            str(output_file),
            config,
            "native",
            None,
            False
        )
        print(f"✓ {source_file.name}: {metrics['input_size']} -> {metrics['output_size']} bytes")
    except Exception as e:
        print(f"✗ {source_file.name}: {e}")
```