#include "ObfuscationPasses.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

// Register passes with the pass manager
llvm::PassPluginLibraryInfo getObfuscatePassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "ObfuscatePasses", LLVM_VERSION_STRING,
    [](PassBuilder &PB) {
      // Register module passes
      PB.registerPipelineParsingCallback(
        [](StringRef Name, ModulePassManager &MPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "string-encrypt") {
            MPM.addPass(obfuscate::StringEncryptionPass());
            return true;
          }
          if (Name == "symbol-rename") {
            MPM.addPass(obfuscate::SymbolRenamingPass());
            return true;
          }
          if (Name == "virtualize") {
            MPM.addPass(obfuscate::FunctionVirtualizationPass());
            return true;
          }
          return false;
        });
      
      // Register function passes
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "junk-insert") {
            FPM.addPass(obfuscate::JunkInsertionPass());
            return true;
          }
          if (Name == "cfg-flatten") {
            FPM.addPass(obfuscate::ControlFlowFlatteningPass());
            return true;
          }
          if (Name == "opaque-predicates") {
            FPM.addPass(obfuscate::OpaquePredicatesPass());
            return true;
          }
          if (Name == "decompiler-adversarial") {
            FPM.addPass(obfuscate::DecompilerAdversarialPass());
            return true;
          }
          return false;
        });
    }
  };
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getObfuscatePassPluginInfo();
}