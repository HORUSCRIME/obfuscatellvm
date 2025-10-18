cmake_minimum_required(VERSION 3.20)

# Find required packages for testing
find_package(GTest QUIET)

if(GTest_FOUND)
    # C++ unit tests
    add_executable(test_passes
        test_passes.cpp
    )
    
    target_link_libraries(test_passes
        obfuscate-passes
        ${llvm_libs}
        GTest::gtest
        GTest::gtest_main
    )
    
    target_include_directories(test_passes PRIVATE
        ../src/passes/include
        ${LLVM_INCLUDE_DIRS}
    )
    
    # Add test
    add_test(NAME PassTests COMMAND test_passes)
else()
    message(WARNING "GTest not found, skipping C++ tests")
endif()

# Python tests (always available)
find_program(PYTHON_EXECUTABLE python3)
if(PYTHON_EXECUTABLE)
    add_test(
        NAME PythonTests
        COMMAND ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test_cli.py -v
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
    
    add_test(
        NAME IntegrationTests  
        COMMAND ${PYTHON_EXECUTABLE} -m pytest ${CMAKE_CURRENT_SOURCE_DIR}/test_integration.py -v
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
endif()