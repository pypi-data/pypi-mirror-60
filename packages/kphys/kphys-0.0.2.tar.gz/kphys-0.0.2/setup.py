# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 20:14:03 2020

@author: karth
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kphys", # Replace with your own username
    version="0.0.2",
    author="Karthik Dulam",
    author_email="karthik.06.dulam@gmail.com",
    description="A small example package for statistical physics on with blender integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/Karthik-Dulam/kphys",
    packages=setuptools.find_packages(),
    license ='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)