"""
Setup configuration for WildGuard-Temporal.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wildguard-temporal",
    version="0.1.0",
    author="Safety Bench Contributors",
    description="AI Safety Persistence Benchmark - Temporal and Contextual Safety Evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathanlubchenco/safety-bench",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "viz": [
            "matplotlib>=3.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ml": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wildguard-temporal=wildguard_temporal.cli:main",
        ],
    },
)
