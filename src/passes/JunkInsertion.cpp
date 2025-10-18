#include "ObfuscationPasses.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include <random>

using namespace llvm;

namespace obfuscate {

PreservedAnalyses JunkInsertionPass::run(Function &F, FunctionAnalysisManager &AM) {
  if (F.isDeclaration())
    return PreservedAnalyses::all();
    
  bool Changed = false;
  std::mt19937 RNG(42);
  
  // Collect original basic blocks
  std::vector<BasicBlock*> OriginalBBs;
  for (auto &BB : F) {
    OriginalBBs.push_back(&BB);
  }
  
  // Insert junk blocks
  for (auto *BB : OriginalBBs) {
    if (RNG() % 10 < 3) { // 30% chance to add junk
      // Create junk basic block
      auto *JunkBB = BasicBlock::Create(F.getContext(), "junk", &F);
      IRBuilder<> Builder(JunkBB);
      
      // Add some junk instructions
      auto *X = Builder.CreateAlloca(Type::getInt32Ty(F.getContext()));
      auto *Y = Builder.CreateAlloca(Type::getInt32Ty(F.getContext()));
      Builder.CreateStore(ConstantInt::get(Type::getInt32Ty(F.getContext()), RNG()), X);
      Builder.CreateStore(ConstantInt::get(Type::getInt32Ty(F.getContext()), RNG()), Y);
      auto *LoadX = Builder.CreateLoad(Type::getInt32Ty(F.getContext()), X);
      auto *LoadY = Builder.CreateLoad(Type::getInt32Ty(F.getContext()), Y);
      auto *Add = Builder.CreateAdd(LoadX, LoadY);
      Builder.CreateStore(Add, X);
      
      // Create opaque predicate (always false: x*x + x is always even)
      auto *Mul = Builder.CreateMul(LoadX, LoadX);
      auto *AddX = Builder.CreateAdd(Mul, LoadX);
      auto *Rem = Builder.CreateSRem(AddX, ConstantInt::get(Type::getInt32Ty(F.getContext()), 2));
      auto *Cmp = Builder.CreateICmpEQ(Rem, ConstantInt::get(Type::getInt32Ty(F.getContext()), 1));
      
      // Split original block and insert conditional jump
      auto *Term = BB->getTerminator();
      if (Term && !isa<ReturnInst>(Term)) {
        auto *NextBB = BB->splitBasicBlock(Term, "after_junk");
        BB->getTerminator()->eraseFromParent();
        
        IRBuilder<> BBBuilder(BB);
        BBBuilder.CreateCondBr(Cmp, JunkBB, NextBB);
        Builder.CreateBr(NextBB);
        
        Changed = true;
      } else {
        Builder.CreateUnreachable();
      }
    }
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate