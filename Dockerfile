# Production Dockerfile for ObfuscateLLVM
FROM ubuntu:22.04

LABEL maintainer="ObfuscateLLVM Team <info@obfuscatellvm.org>"
LABEL description="Production-quality LLVM-based binary obfuscator"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3.11 \
    python3.11-dev \
    python3-pip \
    mingw-w64 \
    && rm -rf /var/lib/apt/lists/*

# Install LLVM 16
RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/jammy/ llvm-toolchain-jammy-16 main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    llvm-16 \
    llvm-16-dev \
    llvm-16-tools \
    clang-16 \
    clang-tools-16 \
    lld-16 \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for LLVM tools
RUN ln -sf /usr/bin/llvm-config-16 /usr/bin/llvm-config && \
    ln -sf /usr/bin/clang-16 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-16 /usr/bin/clang++ && \
    ln -sf /usr/bin/opt-16 /usr/bin/opt && \
    ln -sf /usr/bin/llc-16 /usr/bin/llc && \
    ln -sf /usr/bin/lld-16 /usr/bin/lld

# Set up Python3.11 as default
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Set environment variables
ENV LLVM_DIR=/usr/lib/llvm-16
ENV PATH="/usr/lib/llvm-16/bin:${PATH}"
ENV CC=clang-16
ENV CXX=clang++-16

# Create app directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -e .

# Build LLVM passes
RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Create non-root user
RUN useradd -m -u 1000 obfuscate && \
    chown -R obfuscate:obfuscate /app

USER obfuscate

# Expose web UI port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.path.append('/app/src'); from cli.obfuscatellvm import main" || exit 1

# Default command
CMD ["python3", "src/cli/obfuscatellvm.py", "--help"]


