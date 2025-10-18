#include "ObfuscationPasses.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Support/raw_ostream.h"
#include <gtest/gtest.h>

using namespace llvm;
using namespace obfuscate;

class PassTest : public ::testing::Test {
protected:
    void SetUp() override {
        Context = std::make_unique<LLVMContext>();
        M = std::make_unique<Module>("test", *Context);
    }
    
    std::unique_ptr<LLVMContext> Context;
    std::unique_ptr<Module> M;
};

TEST_F(PassTest, StringEncryptionBasic) {
    // Create a global string
    auto *StrType = ArrayType::get(Type::getInt8Ty(*Context), 6);
    auto *StrInit = ConstantDataArray::getString(*Context, "hello", false);
    auto *GV = new GlobalVariable(*M, StrType, true, GlobalValue::InternalLinkage, StrInit, "test_str");
    
    // Run string encryption pass
    ModuleAnalysisManager MAM;
    StringEncryptionPass Pass;
    auto PA = Pass.run(*M, MAM);
    
    // Verify module is still valid
    EXPECT_FALSE(verifyModule(*M, &errs()));
    
    // Check that pass made changes
    EXPECT_FALSE(PA.areAllPreserved());
}

TEST_F(PassTest, JunkInsertionBasic) {
    // Create a simple function
    auto *FuncType = FunctionType::get(Type::getVoidTy(*Context), false);
    auto *Func = Function::Create(FuncType, Function::InternalLinkage, "test_func", M.get());
    auto *BB = BasicBlock::Create(*Context, "entry", Func);
    
    IRBuilder<> Builder(BB);
    Builder.CreateRetVoid();
    
    // Run junk insertion pass
    FunctionAnalysisManager FAM;
    JunkInsertionPass Pass;
    auto PA = Pass.run(*Func, FAM);
    
    // Verify function is still valid
    EXPECT_FALSE(verifyFunction(*Func, &errs()));
}

TEST_F(PassTest, SymbolRenamingBasic) {
    // Create an internal function
    auto *FuncType = FunctionType::get(Type::getVoidTy(*Context), false);
    auto *Func = Function::Create(FuncType, Function::InternalLinkage, "original_name", M.get());
    auto *BB = BasicBlock::Create(*Context, "entry", Func);
    
    IRBuilder<> Builder(BB);
    Builder.CreateRetVoid();
    
    std::string OriginalName = Func->getName().str();
    
    // Run symbol renaming pass
    ModuleAnalysisManager MAM;
    SymbolRenamingPass Pass;
    auto PA = Pass.run(*M, MAM);
    
    // Verify module is still valid
    EXPECT_FALSE(verifyModule(*M, &errs()));
    
    // Check that name was changed
    EXPECT_NE(Func->getName().str(), OriginalName);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}