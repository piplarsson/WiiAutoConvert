"""
Setup script for WiiAutoConvert
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from src/__init__.py
version = "1.1.0"
try:
    with open(Path(__file__).parent / "src" / "__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break
except:
    pass

# Read README
readme = ""
try:
    with open(Path(__file__).parent / "README.md", encoding="utf-8") as f:
        readme = f.read()
except:
    pass

setup(
    name="wii-autoconvert",
    version=version,
    description="Convert Nintendo Wii RVZ ROMs to WBFS format",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="WiiAutoConvert",
    url="https://github.com/yourusername/wii-autoconvert",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "customtkinter>=5.2.0",
        "tkinterdnd2>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "rvz2wbfs=src.cli:main",
            "wii-autoconvert=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
)

