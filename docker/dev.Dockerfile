FROM ubuntu:22.04

# Prevent interactive prompts during package installation
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
    wine64 \
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
    ln -sf /usr/bin/lld-16 /usr/bin/lld && \
    ln -sf /usr/bin/ld.lld-16 /usr/bin/ld.lld

# Install Python packages
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install \
    click \
    jinja2 \
    pytest \
    pytest-cov \
    black \
    mypy \
    flask

# Set up Python3.11 as default python3
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Set environment variables
ENV LLVM_DIR=/usr/lib/llvm-16
ENV PATH="/usr/lib/llvm-16/bin:${PATH}"
ENV CC=clang-16
ENV CXX=clang++-16

# Create workspace
WORKDIR /workspace

# Verify installation
RUN llvm-config --version && \
    clang --version && \
    python3 --version && \
    cmake --version

CMD ["/bin/bash"]