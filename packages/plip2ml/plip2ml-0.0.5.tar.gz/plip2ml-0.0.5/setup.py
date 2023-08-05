#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plip2ml",
    version="0.0.5",
    author="Mathieu Voland",
    author_email="mathieu.voland@gmail.com",
    description="Using PLIP output as ML input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mvoland/plip2ml",
    packages=['plip2ml'],
    scripts=['bin/plip2ml-xml2csv'],
    install_requires=['pandas>=0.20', 'lxml>=4.0.0'],
    setup_requires=["pytest-runner"],
    tests_require=["pytest>=v4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
