"""
Setup script for HLS Converter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Read version from __init__.py
version = {}
with open("hls_converter/__init__.py") as fp:
    exec(fp.read(), version)

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="hls-converter",
    version=version['__version__'],
    author="HLS Converter Team",
    author_email="",
    description="Professional HLS (HTTP Live Streaming) converter with automatic optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/hls-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.23.0",
            "mkdocstrings-python>=1.7.0",
            "pymdown-extensions>=10.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "hls-converter=hls_converter.cli:main",
            "hlsc=hls_converter.cli:main",  # Short alias
        ],
    },
    keywords=[
        "hls", "http-live-streaming", "video", "streaming", "ffmpeg", 
        "transcoding", "adaptive-bitrate", "m3u8", "video-processing"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/hls-converter/issues",
        "Source": "https://github.com/your-username/hls-converter",
        "Documentation": "https://hls-converter.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)