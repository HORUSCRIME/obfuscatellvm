#include "ObfuscationPasses.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Analysis/ProfileSummaryInfo.h"
#include <random>

using namespace llvm;

namespace obfuscate {

// Simple VM opcodes
enum VMOpcode {
  VM_LOAD = 1,
  VM_STORE = 2,
  VM_ADD = 3,
  VM_SUB = 4,
  VM_MUL = 5,
  VM_RET = 6
};

static bool isColdFunction(Function &F, FunctionAnalysisManager &AM) {
  // Simple heuristic: small functions with no loops are candidates
  if (F.size() > 5) return false;
  
  for (auto &BB : F) {
    for (auto &I : BB) {
      if (isa<CallInst>(I) || isa<InvokeInst>(I)) {
        return false; // Skip functions with calls
      }
    }
  }
  return true;
}

static std::vector<uint8_t> generateBytecode(Function &F) {
  std::vector<uint8_t> bytecode;
  
  // Simple bytecode generation for basic arithmetic
  for (auto &BB : F) {
    for (auto &I : BB) {
      if (auto *Add = dyn_cast<AddInst>(&I)) {
        bytecode.push_back(VM_ADD);
      } else if (auto *Sub = dyn_cast<SubInst>(&I)) {
        bytecode.push_back(VM_SUB);
      } else if (auto *Mul = dyn_cast<MulInst>(&I)) {
        bytecode.push_back(VM_MUL);
      } else if (isa<ReturnInst>(&I)) {
        bytecode.push_back(VM_RET);
      }
    }
  }
  
  return bytecode;
}

PreservedAnalyses FunctionVirtualizationPass::run(Module &M, ModuleAnalysisManager &AM) {
  bool Changed = false;
  std::mt19937 RNG(42);
  
  // Get or create VM interpreter function
  auto *VMFunc = M.getFunction("vm_interpret");
  if (!VMFunc) {
    auto *VMFuncType = FunctionType::get(
      Type::getInt32Ty(M.getContext()),
      {Type::getInt8PtrTy(M.getContext()), Type::getInt32Ty(M.getContext())},
      false);
    VMFunc = Function::Create(VMFuncType, Function::ExternalLinkage, "vm_interpret", M);
  }
  
  // Collect functions to virtualize
  std::vector<Function*> ToVirtualize;
  for (auto &F : M) {
    if (!F.isDeclaration() && F.getName() != "main" && F.getName() != "vm_interpret") {
      FunctionAnalysisManager FAM;
      if (isColdFunction(F, FAM) && RNG() % 10 < 3) { // 30% chance
        ToVirtualize.push_back(&F);
      }
    }
  }
  
  // Virtualize selected functions
  for (auto *F : ToVirtualize) {
    // Generate bytecode
    auto bytecode = generateBytecode(*F);
    if (bytecode.empty()) continue;
    
    // Create bytecode global
    auto *BytecodeArray = ConstantDataArray::get(M.getContext(), bytecode);
    auto *BytecodeGV = new GlobalVariable(
      M, BytecodeArray->getType(), true, GlobalValue::InternalLinkage,
      BytecodeArray, F->getName() + ".bytecode");
    
    // Replace function body with VM call
    F->deleteBody();
    auto *EntryBB = BasicBlock::Create(M.getContext(), "entry", F);
    IRBuilder<> Builder(EntryBB);
    
    auto *VMCall = Builder.CreateCall(VMFunc, {
      Builder.CreateBitCast(BytecodeGV, Type::getInt8PtrTy(M.getContext())),
      ConstantInt::get(Type::getInt32Ty(M.getContext()), bytecode.size())
    });
    
    if (F->getReturnType()->isVoidTy()) {
      Builder.CreateRetVoid();
    } else {
      Builder.CreateRet(VMCall);
    }
    
    Changed = true;
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate