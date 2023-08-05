#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SCPSyncer",
    version="0.1",
    packages=find_packages(),
    install_requires=['paramiko', 'scp', 'PyYAML', 'colorama'],

    long_description=long_description,
    long_description_content_type="text/markdown",
    # metadata to display on PyPI
    author="Frederic98",
    description="SCP syncer",
    keywords="scp sync syncer",
    url="https://github.com/Frederic98/SCP-Syncer"
)
