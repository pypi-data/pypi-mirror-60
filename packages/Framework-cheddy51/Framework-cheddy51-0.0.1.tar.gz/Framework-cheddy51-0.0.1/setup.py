# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    longDescription = fh.read()

setuptools.setup(
    name="Framework-cheddy51",
    version="0.0.1",
    author="Edward Mansfield",
    author_email="emansfield@neuvoapps.com",
    description="A simple python framework for client/server applications",
    long_description=longDescription,
    url="https://github/cheddy51/Framework",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='<=3.6'
)
