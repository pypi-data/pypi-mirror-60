#!/usr/bin/env python
# coding=utf-8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Constrained_GaussianProcess",
    version="0.0.1",
    author="Liaowang Huang",
    author_email="liahuang@student.ethz.ch",
    description="Python implementation of 'Finite-Dimensional Gaussian Approximation with Linear Inequality Constraints'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liaowangh/constrained_gp",
    packages=setuptools.find_packages(),
    calssifiers=[
        "Programming Language :: Python :: 3",
        "Lincense :: OSI Approved :: MIT Lincense",
        "Operating System :: OS Independent",
    ],
    python_requires= '>=3.6',
)
