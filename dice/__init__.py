"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

from sys import argv

from pyparsing import ParseException

from dice.grammar import expression

__all__ = ['roll', 'main', 'ParseException']

def roll(string):
    return expression.parseString(string, parseAll=True)

def main(argv=argv):
    return roll(argv)
