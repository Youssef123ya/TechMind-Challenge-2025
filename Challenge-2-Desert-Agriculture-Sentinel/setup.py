#!/usr/bin/env python3
"""
Setup script for Desert Agriculture Sentinel
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="desert-agriculture-sentinel",
    version="1.0.0",
    author="Desert Agriculture Sentinel Team",
    author_email="info@desert-agriculture-sentinel.org",
    description="Intelligent satellite-based crop health monitoring and water optimization system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Youssef123ya/Challenge-2-Desert-Agriculture-Sentinel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "isort>=5.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "sphinx-autodoc-typehints>=1.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "desert-agriculture-sentinel=main:main",
            "das-download=scripts.download_data:main",
            "das-train=scripts.train_models:main",
            "das-report=scripts.water_report:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "*.md", "*.txt"],
    },
    keywords="agriculture, satellite, remote sensing, machine learning, water optimization, desert farming",
    project_urls={
        "Bug Reports": "https://github.com/Youssef123ya/Challenge-2-Desert-Agriculture-Sentinel/issues",
        "Source": "https://github.com/Youssef123ya/Challenge-2-Desert-Agriculture-Sentinel",
        "Documentation": "https://github.com/Youssef123ya/Challenge-2-Desert-Agriculture-Sentinel/wiki",
    },
)
