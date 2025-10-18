#include "ObfuscationPasses.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include <random>

using namespace llvm;

namespace obfuscate {

// Generate opaque predicate that always evaluates to true
static Value* createAlwaysTruePredicate(IRBuilder<> &Builder, std::mt19937 &RNG) {
  auto *IntTy = Type::getInt32Ty(Builder.getContext());
  
  // Use mathematical identities: (x*x + x) % 2 == 0 for even x
  auto *X = ConstantInt::get(IntTy, (RNG() % 100) * 2); // Even number
  auto *XSquared = Builder.CreateMul(X, X);
  auto *XSquaredPlusX = Builder.CreateAdd(XSquared, X);
  auto *Rem = Builder.CreateSRem(XSquaredPlusX, ConstantInt::get(IntTy, 2));
  return Builder.CreateICmpEQ(Rem, ConstantInt::get(IntTy, 0));
}

// Generate opaque predicate that always evaluates to false
static Value* createAlwaysFalsePredicate(IRBuilder<> &Builder, std::mt19937 &RNG) {
  auto *IntTy = Type::getInt32Ty(Builder.getContext());
  
  // Use mathematical identities: (x*x + x + 1) % 2 == 0 is always false for even x
  auto *X = ConstantInt::get(IntTy, (RNG() % 100) * 2); // Even number
  auto *XSquared = Builder.CreateMul(X, X);
  auto *XSquaredPlusX = Builder.CreateAdd(XSquared, X);
  auto *XSquaredPlusXPlus1 = Builder.CreateAdd(XSquaredPlusX, ConstantInt::get(IntTy, 1));
  auto *Rem = Builder.CreateSRem(XSquaredPlusXPlus1, ConstantInt::get(IntTy, 2));
  return Builder.CreateICmpEQ(Rem, ConstantInt::get(IntTy, 0));
}

PreservedAnalyses OpaquePredicatesPass::run(Function &F, FunctionAnalysisManager &AM) {
  if (F.isDeclaration())
    return PreservedAnalyses::all();
    
  bool Changed = false;
  std::mt19937 RNG(42);
  
  // Collect branch instructions
  std::vector<BranchInst*> Branches;
  for (auto &BB : F) {
    for (auto &I : BB) {
      if (auto *Br = dyn_cast<BranchInst>(&I)) {
        if (Br->isConditional()) {
          Branches.push_back(Br);
        }
      }
    }
  }
  
  // Replace some branch conditions with opaque predicates
  for (auto *Br : Branches) {
    if (RNG() % 10 < 3) { // 30% chance
      IRBuilder<> Builder(Br);
      
      Value *OriginalCond = Br->getCondition();
      Value *OpaquePred;
      
      if (RNG() % 2) {
        // Always true predicate
        OpaquePred = createAlwaysTruePredicate(Builder, RNG);
        // Combine with original: (original && true) == original
        auto *NewCond = Builder.CreateAnd(OriginalCond, OpaquePred);
        Br->setCondition(NewCond);
      } else {
        // Always false predicate  
        OpaquePred = createAlwaysFalsePredicate(Builder, RNG);
        // Combine with original: (original || false) == original
        auto *NewCond = Builder.CreateOr(OriginalCond, OpaquePred);
        Br->setCondition(NewCond);
      }
      
      Changed = true;
    }
  }
  
  // Insert opaque predicates in basic blocks
  for (auto &BB : F) {
    if (RNG() % 10 < 2) { // 20% chance
      auto *Term = BB.getTerminator();
      if (Term && !isa<ReturnInst>(Term)) {
        IRBuilder<> Builder(&BB);
        Builder.SetInsertPoint(Term);
        
        // Create fake conditional that never executes
        auto *FakeCond = createAlwaysFalsePredicate(Builder, RNG);
        auto *FakeBB = BasicBlock::Create(F.getContext(), "fake", &F);
        
        // Add some fake instructions
        IRBuilder<> FakeBuilder(FakeBB);
        auto *FakeVar = FakeBuilder.CreateAlloca(Type::getInt32Ty(F.getContext()));
        FakeBuilder.CreateStore(ConstantInt::get(Type::getInt32Ty(F.getContext()), RNG()), FakeVar);
        FakeBuilder.CreateUnreachable();
        
        // Split block and insert fake branch
        auto *NextBB = BB.splitBasicBlock(Term, "after_fake");
        BB.getTerminator()->eraseFromParent();
        
        IRBuilder<> BBBuilder(&BB);
        BBBuilder.CreateCondBr(FakeCond, FakeBB, NextBB);
        
        Changed = true;
      }
    }
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate