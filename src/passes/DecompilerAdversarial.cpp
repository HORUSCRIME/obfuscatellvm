#include "ObfuscationPasses.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/InlineAsm.h"
#include <random>

using namespace llvm;

namespace obfuscate {

// Anti-Ghidra patterns that confuse decompiler heuristics
static void insertAntiGhidraPattern(BasicBlock *BB, IRBuilder<> &Builder, std::mt19937 &RNG) {
  // Pattern 1: Fake function pointer with indirect call
  auto *IntTy = Type::getInt32Ty(BB->getContext());
  auto *PtrTy = Type::getInt8PtrTy(BB->getContext());
  
  // Create fake function pointer calculation
  auto *Base = ConstantInt::get(IntTy, 0x400000 + (RNG() % 0x100000));
  auto *Offset = ConstantInt::get(IntTy, RNG() % 1000);
  auto *FakeAddr = Builder.CreateAdd(Base, Offset);
  auto *FakePtr = Builder.CreateIntToPtr(FakeAddr, PtrTy);
  
  // Create unreachable indirect call that confuses control flow analysis
  auto *FakeCond = Builder.CreateICmpEQ(
    ConstantInt::get(IntTy, 1), 
    ConstantInt::get(IntTy, 0)  // Always false
  );
  
  auto *FakeBB = BasicBlock::Create(BB->getContext(), "fake_call", BB->getParent());
  auto *ContBB = BasicBlock::Create(BB->getContext(), "continue", BB->getParent());
  
  Builder.CreateCondBr(FakeCond, FakeBB, ContBB);
  
  // In fake block, create confusing indirect call
  IRBuilder<> FakeBuilder(FakeBB);
  auto *FuncTy = FunctionType::get(Type::getVoidTy(BB->getContext()), false);
  auto *FakeFuncPtr = FakeBuilder.CreateBitCast(FakePtr, FuncTy->getPointerTo());
  FakeBuilder.CreateCall(FuncTy, FakeFuncPtr);
  FakeBuilder.CreateUnreachable();
  
  // Continue in real block
  Builder.SetInsertPoint(ContBB);
}

// Anti-Hex-Rays patterns that break decompiler assumptions
static void insertAntiHexRaysPattern(BasicBlock *BB, IRBuilder<> &Builder, std::mt19937 &RNG) {
  // Pattern 2: Stack manipulation that confuses variable tracking
  auto *IntTy = Type::getInt32Ty(BB->getContext());
  
  // Create fake stack frame manipulation
  auto *StackVar1 = Builder.CreateAlloca(IntTy);
  auto *StackVar2 = Builder.CreateAlloca(IntTy);
  
  // Complex pointer arithmetic that breaks alias analysis
  auto *Ptr1 = Builder.CreateBitCast(StackVar1, Type::getInt8PtrTy(BB->getContext()));
  auto *Ptr2 = Builder.CreateBitCast(StackVar2, Type::getInt8PtrTy(BB->getContext()));
  
  auto *Offset = ConstantInt::get(Type::getInt64Ty(BB->getContext()), RNG() % 16);
  auto *OffsetPtr = Builder.CreateGEP(Type::getInt8Ty(BB->getContext()), Ptr1, Offset);
  
  // Store and load through offset pointer to confuse data flow
  Builder.CreateStore(ConstantInt::get(IntTy, RNG()), 
                     Builder.CreateBitCast(OffsetPtr, IntTy->getPointerTo()));
  
  auto *LoadedVal = Builder.CreateLoad(IntTy, 
                     Builder.CreateBitCast(OffsetPtr, IntTy->getPointerTo()));
  
  // Use loaded value in meaningless computation
  auto *Result = Builder.CreateAdd(LoadedVal, ConstantInt::get(IntTy, 42));
  Builder.CreateStore(Result, StackVar2);
}

// Pattern that breaks both Ghidra and Hex-Rays
static void insertUniversalAntiPattern(BasicBlock *BB, IRBuilder<> &Builder, std::mt19937 &RNG) {
  // Pattern 3: Exception handling confusion
  auto *IntTy = Type::getInt32Ty(BB->getContext());
  
  // Create fake exception-like control flow
  auto *ExceptionFlag = Builder.CreateAlloca(IntTy);
  Builder.CreateStore(ConstantInt::get(IntTy, 0), ExceptionFlag);
  
  // Fake try-catch pattern with computed goto
  auto *TryBB = BasicBlock::Create(BB->getContext(), "fake_try", BB->getParent());
  auto *CatchBB = BasicBlock::Create(BB->getContext(), "fake_catch", BB->getParent());
  auto *FinallyBB = BasicBlock::Create(BB->getContext(), "fake_finally", BB->getParent());
  
  // Jump to try block
  Builder.CreateBr(TryBB);
  
  // Try block with fake exception
  IRBuilder<> TryBuilder(TryBB);
  auto *FakeException = TryBuilder.CreateLoad(IntTy, ExceptionFlag);
  auto *ExceptionCond = TryBuilder.CreateICmpNE(FakeException, ConstantInt::get(IntTy, 0));
  TryBuilder.CreateCondBr(ExceptionCond, CatchBB, FinallyBB);
  
  // Catch block (never executed)
  IRBuilder<> CatchBuilder(CatchBB);
  CatchBuilder.CreateStore(ConstantInt::get(IntTy, 1), ExceptionFlag);
  CatchBuilder.CreateBr(FinallyBB);
  
  // Finally block continues execution
  Builder.SetInsertPoint(FinallyBB);
}

PreservedAnalyses DecompilerAdversarialPass::run(Function &F, FunctionAnalysisManager &AM) {
  if (F.isDeclaration())
    return PreservedAnalyses::all();
    
  bool Changed = false;
  std::mt19937 RNG(42);
  
  // Apply adversarial patterns to random basic blocks
  std::vector<BasicBlock*> Blocks;
  for (auto &BB : F) {
    Blocks.push_back(&BB);
  }
  
  for (auto *BB : Blocks) {
    if (RNG() % 10 < 2) { // 20% chance per block
      auto *Term = BB->getTerminator();
      if (Term && !isa<ReturnInst>(Term)) {
        IRBuilder<> Builder(BB);
        Builder.SetInsertPoint(Term);
        
        int PatternType = RNG() % 3;
        switch (PatternType) {
          case 0:
            insertAntiGhidraPattern(BB, Builder, RNG);
            break;
          case 1:
            insertAntiHexRaysPattern(BB, Builder, RNG);
            break;
          case 2:
            insertUniversalAntiPattern(BB, Builder, RNG);
            break;
        }
        
        Changed = true;
      }
    }
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate