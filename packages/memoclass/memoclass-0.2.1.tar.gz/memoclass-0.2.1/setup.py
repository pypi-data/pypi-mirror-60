#!/usr/bin/env python

from __future__ import absolute_import

from setuptools import find_packages, setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst') ) as f:
    long_description = f.read()

setup(
    name="memoclass",
    version="0.2.1",
    packages=find_packages('src'),
    package_dir={'':'src'},
    license="MIT",
    description="A utility package for memoizing functions and class methods",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Jon Burr",
    author_email="jon.burr.gh@gmail.com",
    keywords=["memoize", "cache"],
    url="https://github.com/Jon-Burr/memoclass.git",
    install_requires=[
        "future",
        'funcsigs;python_version<"3.0"'
        ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        ]
    )
