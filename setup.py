#!/usr/bin/env python3
"""Setup script for ObfuscateLLVM Python package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements = [
    "click>=8.0.0",
    "jinja2>=3.0.0",
    "flask>=2.0.0",
    "numpy>=1.20.0",
    "requests>=2.25.0",
    "cryptography>=3.4.0",
]

dev_requirements = [
    "pytest>=6.0.0",
    "pytest-cov>=2.10.0",
    "black>=21.0.0",
    "mypy>=0.800",
    "flake8>=3.8.0",
]

setup(
    name="obfuscatellvm",
    version="1.0.0",
    description="Production-quality LLVM-based binary obfuscator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ObfuscateLLVM Team",
    author_email="info@obfuscatellvm.org",
    url="https://github.com/obfuscatellvm/obfuscatellvm",
    project_urls={
        "Documentation": "https://obfuscatellvm.readthedocs.io/",
        "Source": "https://github.com/obfuscatellvm/obfuscatellvm",
        "Tracker": "https://github.com/obfuscatellvm/obfuscatellvm/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "obfuscatellvm": [
            "cli/*.py",
            "passes/*.cpp",
            "passes/*.c",
            "passes/*.h",
            "passes/include/*.h",
        ],
    },
    entry_points={
        "console_scripts": [
            "obfuscatellvm=cli.obfuscatellvm:main",
            "obfuscate-marketplace=cli.marketplace:main",
        ],
    },
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "research": ["z3-solver>=4.8.0"],
        "web": ["flask>=2.0.0"],
        "all": requirements + dev_requirements + ["z3-solver>=4.8.0"],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: Security",
        "Topic :: Software Development :: Compilers",
        "Topic :: System :: Software Distribution",
    ],
    keywords="obfuscation llvm compiler security reverse-engineering",
    zip_safe=False,
)