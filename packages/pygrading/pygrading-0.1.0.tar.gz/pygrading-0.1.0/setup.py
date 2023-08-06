"""
    Name: setup.py
    Author: Charles Zhang <694556046@qq.com>
    Propose: Setup script for pygrading!
    Coding: UTF-8

    Change Log:
        **2020.01.29**
        Update version to 0.1.0!

        **2020.01.26**
        Create this file!
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygrading",
    version="0.1.0",
    author="Charles Zhang",
    author_email="694556046@qq.com",
    description="A Python ToolBox for CourseGrading platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhenomingZ/PyGrading",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
