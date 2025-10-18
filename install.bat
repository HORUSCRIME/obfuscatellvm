@echo off
REM ObfuscateLLVM Windows Installation Script

echo Installing ObfuscateLLVM dependencies...

REM Check if chocolatey is installed
choco --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Please install Chocolatey first: https://chocolatey.org/install
    exit /b 1
)

REM Install dependencies via chocolatey
echo Installing LLVM and build tools...
choco install -y llvm cmake python3 mingw

REM Install Python dependencies
echo Installing Python packages...
pip install -r requirements.txt

REM Build project
echo Building ObfuscateLLVM...
mkdir build 2>nul
cd build
cmake ..
cmake --build . --config Release

echo Installation complete!
echo Run: python src\cli\obfuscatellvm.py --help