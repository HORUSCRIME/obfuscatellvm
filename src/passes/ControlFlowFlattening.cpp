#include "ObfuscationPasses.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include <random>
#include <vector>

using namespace llvm;

namespace obfuscate {

PreservedAnalyses ControlFlowFlatteningPass::run(Function &F, FunctionAnalysisManager &AM) {
  if (F.isDeclaration() || F.size() < 3)
    return PreservedAnalyses::all();
    
  std::mt19937 RNG(42);
  
  // Collect original basic blocks (skip entry)
  std::vector<BasicBlock*> OriginalBBs;
  for (auto &BB : F) {
    if (&BB != &F.getEntryBlock()) {
      OriginalBBs.push_back(&BB);
    }
  }
  
  if (OriginalBBs.empty())
    return PreservedAnalyses::all();
  
  // Create dispatcher block
  BasicBlock *DispatchBB = BasicBlock::Create(F.getContext(), "dispatch", &F);
  IRBuilder<> DispatchBuilder(DispatchBB);
  
  // Create state variable
  auto *StateVar = DispatchBuilder.CreateAlloca(Type::getInt32Ty(F.getContext()), nullptr, "state");
  
  // Assign random case values to blocks
  std::vector<int> CaseValues;
  for (size_t i = 0; i < OriginalBBs.size(); i++) {
    CaseValues.push_back(RNG() % 1000 + 1);
  }
  
  // Create switch instruction
  auto *Switch = DispatchBuilder.CreateSwitch(
    DispatchBuilder.CreateLoad(Type::getInt32Ty(F.getContext()), StateVar),
    OriginalBBs[0], OriginalBBs.size());
  
  // Process each basic block
  for (size_t i = 0; i < OriginalBBs.size(); i++) {
    BasicBlock *BB = OriginalBBs[i];
    int CaseValue = CaseValues[i];
    
    // Add case to switch
    Switch->addCase(ConstantInt::get(Type::getInt32Ty(F.getContext()), CaseValue), BB);
    
    // Modify block terminator
    auto *Term = BB->getTerminator();
    if (auto *Br = dyn_cast<BranchInst>(Term)) {
      IRBuilder<> Builder(BB);
      Builder.SetInsertPoint(Term);
      
      if (Br->isUnconditional()) {
        // Unconditional branch - set next state and jump to dispatcher
        BasicBlock *Target = Br->getSuccessor(0);
        auto it = std::find(OriginalBBs.begin(), OriginalBBs.end(), Target);
        if (it != OriginalBBs.end()) {
          int NextState = CaseValues[it - OriginalBBs.begin()];
          Builder.CreateStore(ConstantInt::get(Type::getInt32Ty(F.getContext()), NextState), StateVar);
          Builder.CreateBr(DispatchBB);
          Term->eraseFromParent();
        }
      } else {
        // Conditional branch - create conditional state update
        BasicBlock *TrueBB = Br->getSuccessor(0);
        BasicBlock *FalseBB = Br->getSuccessor(1);
        
        auto TrueIt = std::find(OriginalBBs.begin(), OriginalBBs.end(), TrueBB);
        auto FalseIt = std::find(OriginalBBs.begin(), OriginalBBs.end(), FalseBB);
        
        if (TrueIt != OriginalBBs.end() && FalseIt != OriginalBBs.end()) {
          int TrueState = CaseValues[TrueIt - OriginalBBs.begin()];
          int FalseState = CaseValues[FalseIt - OriginalBBs.begin()];
          
          auto *NextState = Builder.CreateSelect(
            Br->getCondition(),
            ConstantInt::get(Type::getInt32Ty(F.getContext()), TrueState),
            ConstantInt::get(Type::getInt32Ty(F.getContext()), FalseState));
          Builder.CreateStore(NextState, StateVar);
          Builder.CreateBr(DispatchBB);
          Term->eraseFromParent();
        }
      }
    }
  }
  
  // Redirect entry block to dispatcher
  BasicBlock *EntryBB = &F.getEntryBlock();
  auto *EntryTerm = EntryBB->getTerminator();
  if (EntryTerm) {
    IRBuilder<> EntryBuilder(EntryBB);
    EntryBuilder.SetInsertPoint(EntryTerm);
    EntryBuilder.CreateStore(ConstantInt::get(Type::getInt32Ty(F.getContext()), CaseValues[0]), StateVar);
    EntryBuilder.CreateBr(DispatchBB);
    EntryTerm->eraseFromParent();
  }
  
  return PreservedAnalyses::none();
}

} // namespace obfuscate