#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals
from setuptools import setup, find_packages

setup(
    name             = 'dice',
    version          = '0.1.7',

    author           = "Sam Clements",
    author_email     = "sam@borntyping.co.uk",
    url              = "https://github.com/borntyping/python-dice",

    description      = "A library for parsing and evaluating dice notation",
    long_description = open('README.rst').read(),

    packages         = find_packages(),
    install_requires = [
        'pyparsing==2.0.1',
        'six==1.3.0'
    ],

    entry_points     = {
        'console_scripts': ['roll = dice:main']
    },

    classifiers     = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)',
        'Topic :: Utilities',
    ],
)
