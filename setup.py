"""
Setup script for aRdent ScanPad Python library
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from package
def read_version():
    version_file = os.path.join("ardent_scanpad", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="ardent-scanpad",
    version=read_version(),
    author="aRdent Solutions",
    author_email="support@ardentsolutions.com",
    description="Python library for aRdent ScanPad BLE HID device",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ardentsolutions/ardent-scanpad-python",
    project_urls={
        "Bug Tracker": "https://github.com/ardentsolutions/ardent-scanpad-python/issues",
        "Documentation": "https://docs.ardentsolutions.com/scanpad",
        "Source Code": "https://github.com/ardentsolutions/ardent-scanpad-python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "bleak>=0.20.0",
        "asyncio>=3.4.3; python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "scanpad-cli=ardent_scanpad.cli:main",
        ],
    },
    keywords=[
        "bluetooth", "ble", "hid", "keyboard", "scanpad", 
        "barcode", "scanner", "ardent", "hardware"
    ],
    license="MIT",
    zip_safe=False,
    include_package_data=True,
    package_data={
        "ardent_scanpad": [
            "py.typed",  # PEP 561 marker file for type hints
        ],
    },
)