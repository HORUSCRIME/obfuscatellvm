#include "ObfuscationPasses.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/GlobalVariable.h"
#include <random>
#include <sstream>

using namespace llvm;

namespace obfuscate {

static std::string generateRandomName(std::mt19937 &RNG) {
  const char chars[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  std::ostringstream name;
  name << "_";
  for (int i = 0; i < 8; i++) {
    name << chars[RNG() % (sizeof(chars) - 1)];
  }
  return name.str();
}

PreservedAnalyses SymbolRenamingPass::run(Module &M, ModuleAnalysisManager &AM) {
  bool Changed = false;
  std::mt19937 RNG(42);
  
  // Rename internal functions
  for (auto &F : M) {
    if (!F.isDeclaration() && F.hasInternalLinkage() && !F.getName().startswith("main")) {
      F.setName(generateRandomName(RNG));
      Changed = true;
    }
  }
  
  // Rename internal global variables
  for (auto &GV : M.globals()) {
    if (GV.hasInternalLinkage() && !GV.getName().empty()) {
      GV.setName(generateRandomName(RNG));
      Changed = true;
    }
  }
  
  // Strip debug metadata
  for (auto &F : M) {
    for (auto &BB : F) {
      for (auto &I : BB) {
        if (I.hasMetadata()) {
          SmallVector<std::pair<unsigned, MDNode*>, 4> MDs;
          I.getAllMetadata(MDs);
          for (auto &MD : MDs) {
            if (MD.first == LLVMContext::MD_dbg) {
              I.setMetadata(MD.first, nullptr);
              Changed = true;
            }
          }
        }
      }
    }
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate