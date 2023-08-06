#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 16:11:17 2020

@author: sajal
"""

import setuptools
with open("README.md", "r") as fh:
    README = fh.read()

setuptools.setup(
    name="topsis101753012", # Replace with your own username
    version="1.0.1",
    author="Sajal Jain",
    author_email="mesajal24@gmail.com",
    description="A Python package to implement topsis function",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mesajal24/topsis_101753012",
    packages=setuptools.find_packages(),
    licence="MIT" 
)