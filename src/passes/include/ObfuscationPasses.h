#pragma once

#include "llvm/IR/PassManager.h"
#include "llvm/Pass.h"

namespace obfuscate {

/// String encryption pass - encrypts global string constants
class StringEncryptionPass : public llvm::PassInfoMixin<StringEncryptionPass> {
public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Junk code insertion pass - adds dead basic blocks and opaque predicates  
class JunkInsertionPass : public llvm::PassInfoMixin<JunkInsertionPass> {
public:
  llvm::PreservedAnalyses run(llvm::Function &F, llvm::FunctionAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Symbol renaming pass - renames local symbols and strips metadata
class SymbolRenamingPass : public llvm::PassInfoMixin<SymbolRenamingPass> {
public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Control flow flattening pass - converts CFG to switch-based dispatcher
class ControlFlowFlatteningPass : public llvm::PassInfoMixin<ControlFlowFlatteningPass> {
public:
  llvm::PreservedAnalyses run(llvm::Function &F, llvm::FunctionAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Opaque predicates pass - replaces conditions with complex expressions
class OpaquePredicatesPass : public llvm::PassInfoMixin<OpaquePredicatesPass> {
public:
  llvm::PreservedAnalyses run(llvm::Function &F, llvm::FunctionAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Function virtualization pass - converts functions to bytecode
class FunctionVirtualizationPass : public llvm::PassInfoMixin<FunctionVirtualizationPass> {
public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &AM);
  static bool isRequired() { return true; }
};

/// Decompiler adversarial pass - targets specific decompiler heuristics
class DecompilerAdversarialPass : public llvm::PassInfoMixin<DecompilerAdversarialPass> {
public:
  llvm::PreservedAnalyses run(llvm::Function &F, llvm::FunctionAnalysisManager &AM);
  static bool isRequired() { return true; }
};

} // namespace obfuscate