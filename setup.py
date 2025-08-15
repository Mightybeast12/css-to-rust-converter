#!/usr/bin/env python3
"""Setup script for CSS-to-Rust converter."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="css-to-rust-converter",
    version="1.0.0",
    author="Firat Honca",
    author_email="firathonca@gmail.com",
    description="Convert CSS styles to Rust stylist format for Yew applications and other Rust projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Web Development",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "css-to-rust=css_to_rust.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "css_to_rust": ["templates/*.j2"],
    },
)
