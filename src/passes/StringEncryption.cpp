#include "ObfuscationPasses.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Support/raw_ostream.h"
#include <random>

using namespace llvm;

namespace obfuscate {

PreservedAnalyses StringEncryptionPass::run(Module &M, ModuleAnalysisManager &AM) {
  bool Changed = false;
  std::mt19937 RNG(42); // Fixed seed for deterministic behavior
  
  for (auto &GV : M.globals()) {
    if (!GV.hasInitializer() || !GV.isConstant())
      continue;
      
    auto *Init = GV.getInitializer();
    if (auto *CDA = dyn_cast<ConstantDataArray>(Init)) {
      if (!CDA->isString())
        continue;
        
      StringRef OrigStr = CDA->getAsString();
      if (OrigStr.size() < 4) // Skip very short strings
        continue;
        
      // Generate XOR key
      uint8_t Key = RNG() & 0xFF;
      
      // Encrypt string
      std::vector<uint8_t> EncryptedData;
      for (char C : OrigStr) {
        EncryptedData.push_back(C ^ Key);
      }
      
      // Create encrypted global
      auto *EncryptedArray = ConstantDataArray::get(M.getContext(), EncryptedData);
      auto *EncryptedGV = new GlobalVariable(
        M, EncryptedArray->getType(), true, GV.getLinkage(),
        EncryptedArray, GV.getName() + ".enc");
        
      // Create key global
      auto *KeyGV = new GlobalVariable(
        M, Type::getInt8Ty(M.getContext()), true, GV.getLinkage(),
        ConstantInt::get(Type::getInt8Ty(M.getContext()), Key),
        GV.getName() + ".key");
        
      // Replace uses with decryption call
      IRBuilder<> Builder(M.getContext());
      auto *DecryptFunc = M.getOrInsertFunction(
        "decrypt_string",
        FunctionType::get(
          Type::getInt8PtrTy(M.getContext()),
          {Type::getInt8PtrTy(M.getContext()), Type::getInt8Ty(M.getContext()), Type::getInt32Ty(M.getContext())},
          false));
          
      // Replace all uses
      for (auto *User : GV.users()) {
        if (auto *Inst = dyn_cast<Instruction>(User)) {
          Builder.SetInsertPoint(Inst);
          auto *DecryptCall = Builder.CreateCall(DecryptFunc, {
            Builder.CreateBitCast(EncryptedGV, Type::getInt8PtrTy(M.getContext())),
            Builder.CreateLoad(Type::getInt8Ty(M.getContext()), KeyGV),
            ConstantInt::get(Type::getInt32Ty(M.getContext()), OrigStr.size())
          });
          Inst->replaceUsesOfWith(&GV, DecryptCall);
        }
      }
      
      GV.eraseFromParent();
      Changed = true;
    }
  }
  
  return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
}

} // namespace obfuscate