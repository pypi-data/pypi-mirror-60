#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 23:11:06 2020

@author: mikeronni
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MicceriRD",
    version="0.2",
    author="Michael Lance",
    author_email="michael.lance@gmail.com",
    description="Real distributions identified by Ted Micceri in his seminal \
    1989 article: The Unicorn, The Normal Curve and Other Improbable Creatures - includes distributions and sampling functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
