#!/usr/bin/env python
from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="alphai",
    version="0.0.2",
    author="Andrew Chang",
    author_email="aychang995@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True
)
