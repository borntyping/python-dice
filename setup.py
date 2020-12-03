#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals
from setuptools import setup, find_packages

setup(
    name="dice",
    version="3.1.1",
    author="Sam Clements",
    author_email="sam@borntyping.co.uk",
    url="https://github.com/borntyping/python-dice",
    description="A library for parsing and evaluating dice notation",
    long_description=open("README.rst").read(),
    license="MIT",
    packages=find_packages(),
    install_requires=["docopt>=0.6.1", "pyparsing>=2.4.1"],
    entry_points={
        "console_scripts": ["dice = dice.command:main", "roll = dice.command:main"]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        "Topic :: Utilities",
    ],
)
