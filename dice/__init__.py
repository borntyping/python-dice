"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import ParseException

from dice.utilities import patch_pyparsing

__all__ = ['roll', 'main', 'ParseException']

patch_pyparsing()

def roll(expression):
    pass

def main():
    pass
