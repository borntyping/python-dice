"""
A library for parsing and evaluating dice notation.

PyParsing is patched to make it easier to work with, by removing features
that get in the way of development and debugging. See the dice.utilities
module for more information.
"""

from __future__ import absolute_import, print_function, unicode_literals

from sys import argv

from pyparsing import ParseException

from dice.grammar import expression
from dice.utilities import patch_pyparsing

__all__ = ['roll', 'main', 'ParseException']

patch_pyparsing()

def roll(string):
    return expression.parseString(string)

def main(argv=argv):
    return roll(' '.join(argv))
