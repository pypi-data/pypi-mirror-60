from setuptools import setup, find_packages
import re

version = re.search(
    r'^__VERSION__\s*=\s*"(.*)"', open("freefall/__init__.py").read(), re.M
).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="freefall",
    version=version,
    packages=find_packages(),
    url="https://github.com/cwstryker/freefall/",
    author="Chadwick Stryker",
    author_email="cwsaccts@stryker5.org",
    description="A Python package module for simulating falling objects with aerodynamic drag.",
    long_description=long_description,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
