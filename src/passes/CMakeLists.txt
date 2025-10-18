cmake_minimum_required(VERSION 3.20)

# Create shared library for obfuscation passes
add_library(obfuscate-passes SHARED
    StringEncryption.cpp
    JunkInsertion.cpp
    SymbolRenaming.cpp
    ControlFlowFlattening.cpp
    OpaquePredicates.cpp
    FunctionVirtualization.cpp
    DecompilerAdversarial.cpp
    PassRegistry.cpp
)

# Create runtime library
add_library(obfuscate-runtime STATIC
    runtime.c
    vm_runtime.c
)

# Link with LLVM libraries
target_link_libraries(obfuscate-passes ${llvm_libs})

# Set properties
set_target_properties(obfuscate-passes PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)

# Include directories
target_include_directories(obfuscate-passes PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${LLVM_INCLUDE_DIRS}
)

# Compiler definitions
target_compile_definitions(obfuscate-passes PRIVATE ${LLVM_DEFINITIONS})

# Install targets
install(TARGETS obfuscate-passes obfuscate-runtime
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)