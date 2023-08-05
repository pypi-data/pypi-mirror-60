#!/usr/bin/env python
import pathlib
import setuptools
#
from pyetldb import pyetldb as module

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setuptools.setup(
    name=module.__project__,
    version=module.__version__,
    author=module.__author__,
    author_email=module.__authoremail__,
    description=module.short_description,
    long_description=README,    
    long_description_content_type="text/markdown",
    url=module.__source__,
    packages=setuptools.find_packages(exclude=("tests",)),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cx-Oracle",
        "mysqlclient",
        "psycopg2",
        "pyodbc",
        "pypyodbc"
    ]
)