#!/bin/bash
# Test script for Docker environment

set -e

echo "=== ObfuscateLLVM Docker Test ==="

# Build the project
echo "Building project..."
mkdir -p build
cd build
cmake ..
make -j$(nproc)
cd ..

echo "Build completed successfully!"

# Test CLI
echo "Testing CLI..."
python src/cli/obfuscatellvm.py --help

# Test obfuscation pipeline
echo "Testing obfuscation pipeline..."
python src/cli/obfuscatellvm.py \
    --input examples/hello.c \
    --output hello_obf \
    --profile balanced \
    --report report.json \
    --verbose

echo "Checking output..."
if [ -f hello_obf ]; then
    echo "✓ Obfuscated binary created"
    ls -la hello_obf
else
    echo "✗ Obfuscated binary not found"
fi

if [ -f report.json ]; then
    echo "✓ Report generated"
    cat report.json
else
    echo "✗ Report not found"
fi

# Test original vs obfuscated
echo "Testing original program..."
clang examples/hello.c -o hello_orig
./hello_orig

if [ -f hello_obf ]; then
    echo "Testing obfuscated program..."
    ./hello_obf
fi

echo "=== Test completed ==="